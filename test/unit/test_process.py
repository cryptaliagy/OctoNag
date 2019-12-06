import pytest
from unittest.mock import patch
from functools import partial
from octonag.main import get_user_ids
from octonag.main import process
from octonag.messages import was_assigned
from octonag.messages import review_made
import logging

log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)


class Response:
    def __init__(self, status_code=200):
        self.status_code = status_code


# General variables
user_list = [{
    'login': 'asdqwe',
    'name': 'asdqw00eqw',
    'email': 'asdqwon@saodnqwe.com'
}, {
    'login': 'asdqqweqe',
    'name': 'asdqw0afqdw0eqw',
    'email': 'asdqwasdon@saodnqwe.com'
}, {
    'login': 'qweqwe',
    'name': 'afwqrqweqw',
    'email': 'qweasdqweqweasfqwerqw@sjapweqwe.com'
}]
user_ids = ['ASDQWEJPFFDQWE', 'ASDQWENASFQJWE', 'ASDQWENINJ']
email_to_id_table = {
    user['email']: uid for user, uid in zip(user_list, user_ids)
}
email_to_id_table['author@email.com'] = 'ABCDEFG'
author_email = "author@email.com"
author_uid = 'ABCDEFG'
reviewed = partial(review_made, title="Test", url="www.test.com")
assigned = partial(was_assigned, author='Steve', title='Test', url='www.test.com')


# Process test cases
is_draft_pr = {
    'is_draft': True
}
has_no_assigned_or_reviewers = {}
has_only_assigned = {
    'has_assigned': True
}
has_only_requested = {
    'has_reviewers': True
}
has_assigned_and_reviewers = {
    'has_assigned': True,
    'has_reviewers': True,
}
pr_was_approved = {
    'final_state': 'APPROVED'
}
pr_was_not_approved = {
    'final_state': 'CHANGES_REQUESTED'
}


def lookup_user_mock(login, email, name):
    return email_to_id_table[email]


def build_pr_data(is_draft=False, final_state=None,
                  has_reviewers=False, has_assigned=False
                  ):
    return {
        'isDraft': is_draft,
        'author': {
            'login': 'stevestevenson',
            'email': 'author@email.com',
            'name': 'Steve',
        },
        'url': 'www.test.com',
        'title': 'Test',
        'assignees': {
            'nodes': user_list if has_assigned else []
        },
        'reviewRequests': {
            'nodes': [
                {'requestedReviewer': user} for user in user_list
            ] if has_reviewers else []
        },
        'reviews': {
            'nodes': [
                {'state': final_state},
                {'state': 'APPROVED'},
                {'state': 'CHANGES_REQUESTED'},
                {'state': 'CHANGES_REQUESTED'},
                {'state': 'CHANGES_REQUESTED'},
                {'state': 'APPROVED'},
                {'state': 'CHANGES_REQUESTED'},
            ] if final_state else []
        },
    }


@pytest.mark.unit
@pytest.mark.parametrize("test_input,lookup_user_returns,expected", [
    ([], lambda x, y, z: None, set()),
    (user_list, user_ids, {*user_ids}),
    ([{'requestedReviewer': user} for user in user_list], user_ids, {*user_ids}),
    (user_list, [None, None, None], set())
])
def test_get_user_ids(test_input, lookup_user_returns, expected):
    with patch('octonag.main.lookup_user') as lookup_user:
        log.debug(lookup_user_returns)
        lookup_user.side_effect = lookup_user_returns

        result = get_user_ids(user_list)

    assert result == expected


@pytest.mark.unit
@pytest.mark.parametrize("test_state,expected", [
    ([
        {'state': 'APPROVED'},
        {'state': 'CHANGES_REQUESTED'},
        {'state': 'CHANGES_REQUESTED'},
        {'state': 'CHANGES_REQUESTED'},
        {'state': 'CHANGES_REQUESTED'},
    ], 'APPROVED'),
    ([
        {'state': 'CHANGES_REQUESTED'},
        {'state': 'CHANGES_REQUESTED'},
        {'state': 'CHANGES_REQUESTED'},
        {'state': 'APPROVED'},
        {'state': 'CHANGES_REQUESTED'},
    ], 'CHANGES_REQUESTED'),
])
def test_state_reducer(test_state, expected):
    from octonag.main import state_reducer
    from functools import reduce

    state = reduce(state_reducer, test_state, test_state[0]['state'])

    assert state == expected


@pytest.mark.unit
@pytest.mark.parametrize('pr_data_schema,expected_return', [
    (is_draft_pr, None),
    (has_no_assigned_or_reviewers, [
        ({author_uid}, reviewed(has_reviewers_assigned=False))
    ]),
    (has_only_requested, [
        ({*user_ids}, assigned(review_request=True))
    ]),
    (has_only_assigned, [
        ({*user_ids}, assigned())
    ]),
    (has_assigned_and_reviewers, [
        ({*user_ids}, assigned()),
        (set(), assigned(review_request=True))
    ]),
    (pr_was_approved, [
        ({author_uid}, reviewed(has_reviewers_assigned=True, approved=True))
    ]),
    (pr_was_not_approved, [
        ({author_uid}, reviewed(has_reviewers_assigned=True, approved=False))
    ])
])
def test_process(pr_data_schema, expected_return):
    with patch('octonag.main.lookup_user') as lookup_user:
        lookup_user.side_effect = lookup_user_mock

        pr_data = build_pr_data(**pr_data_schema)

        result = process(pr_data)
    if result is None:
        assert result == expected_return
    else:
        assert len(result) == len(expected_return)
        for r, e in zip(result, expected_return):
            assert r == e

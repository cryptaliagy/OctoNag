from .queries import build_query
from .queries import run_query
from .messages import greet
from .messages import was_assigned
from .messages import review_made
from .messages import GOODBYE_MSG as goodbye
from .slack import lookup_user
from .slack import msg_user
from .slack import get_name_from_id
from .jira_status import in_review
from .configuration import use_jira
from .configuration import ignore_requested
from .configuration import ignore_assigned
from .configuration import send_greeting
from collections import deque
from pprint import pprint
from functools import partial
from functools import reduce


def process(pr_data):
    '''
    Returns a list of tuples containing a set of targets and a message
    for the targets
    '''
    if pr_data['isDraft'] is True:
        return None  # Do not check for empty PRs

    author_login = pr_data['author']['login']
    author_email = pr_data['author'].get('email', None)
    author_name = pr_data['author'].get('name', author_login)
    url = pr_data['url']
    title = pr_data['title']
    assignees = pr_data['assignees']['nodes']
    reviewers = pr_data['reviewRequests']['nodes']
    review_states = pr_data['reviews']['nodes']

    author_id = lookup_user(author_login, author_email, author_name)
    assignee_ids = get_user_ids(assignees)  # Converts to a set for faster lookup
    reviewer_ids = get_user_ids(reviewers)  # Converts to a set for faster lookup

    if not author_name:
        author_name = author_login

    reviewed = partial(review_made, title=title, url=url)
    assigned = partial(was_assigned, author=author_name, title=title, url=url)

    result = []

    if len(review_states) > 0:
        state = \
            reduce(state_reducer, review_states, review_states[0]['state'])

        if state == 'CHANGES_REQUESTED' and author_id is not None:
            target = {author_id}
            msg = reviewed(has_reviewers_assigned=True)
            result.append((target, msg))
        elif state == 'APPROVED' and author_id is not None:
            target = {author_id}
            msg = reviewed(has_reviewers_assigned=True, approved=True)
            result.append((target, msg))
        elif state != 'APPROVED':
            if len(assignee_ids) > 0:
                assigned_msg = assigned()
                result.append((assignee_ids, assigned_msg))

            requested_target = reviewer_ids - assignee_ids

            if len(requested_target) > 0:
                requested_msg = assigned(review_request=True)
                result.append((requested_target, requested_msg))
    else:
        if len(assignee_ids) > 0 and not ignore_requested:
            msg = assigned()
            result.append((assignee_ids, msg))

        if len(reviewer_ids) > 0 and not ignore_assigned:
            msg = assigned(review_request=True)
            only_requested = reviewer_ids - assignee_ids
            result.append((only_requested, msg))

        if len(assignees) == 0 and len(reviewers) == 0 and \
            author_id is not None and not ignore_requested and \
                not ignore_assigned:
            target = {author_id}
            msg = reviewed(has_reviewers_assigned=False)
            result.append((target, msg))

    return result


def get_user_ids(users_list):
    result = set()
    for user in users_list:
        if 'requestedReviewer' in user:
            user = user['requestedReviewer']
        uid = None
        if user is not None:
            login = user['login']
            email = user['email']
            name = user['name']
            uid = lookup_user(login, email, name)
        if uid is not None:
            result.add(lookup_user(login, email, name))
    return result


def state_reducer(accumulated, current_state):
    if current_state['state'] not in ['CHANGES_REQUESTED', 'APPROVED']:
        return current_state['state']
    return accumulated


def msg_all_enqueued(msg_queue):
    messaged = set()
    total = 0
    while len(msg_queue) > 0:
        targets, message = msg_queue.popleft()

        for target in targets:
            if target not in messaged and send_greeting:
                name = get_name_from_id(target)
                greeting = greet(name)
                msg_user(target, greeting)
                messaged.add(target)
            msg_user(target, message)
            total += 1

    if send_greeting:
        for user in messaged:
            msg_user(user, goodbye)

    return messaged, total


def main():
    msg_queue = deque()
    query = build_query()
    result = run_query(query)

    if 'errors' in result:
        pprint(result)
        raise Exception('Something went wrong with the query')

    result = result['data']

    for key in result:
        pull_requests = result[key]['pullRequests']['nodes']
        for pull_request in pull_requests:
            if use_jira:
                review_status = in_review(pull_request['branch'])
                if review_status is False:  # Don't skip if returns None
                    continue
            targets = process(pull_request)
            if targets is not None:
                msg_queue.extend(targets)

    unique_nags, total_nags = msg_all_enqueued(msg_queue)
    print('OctoNag has finished nagging for the day!')
    print('Sent %d nags to a total of %d people' % (total_nags, len(unique_nags)))
    print('Nagged people:', *map(get_name_from_id, unique_nags))


if __name__ == "__main__":
    main()

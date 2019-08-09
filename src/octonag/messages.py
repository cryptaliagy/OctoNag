from string import Template

HELLO_TEMPLATE = \
    Template('Hello $name! Here\'s a summary of your pending Pull Request actions:')
REVIEWED_PR_TEMPLATE = \
    Template('Your pull request \"$title\" ($url) has been reviewed but *not approved*.')
REQUESTED_REVIEWER_TEMPLATE = \
    Template('You are a *requested reviewer* on $author\'s pull request \"$title\" ($url), which is still awaiting approval.')  # noqa: E501
NO_REVIEWERS_TEMPLATE = \
    Template('You *haven\'t requested any reviewers, or assigned someone* on pull request \"$title\" ($url).')  # noqa: E501
REQUESTED_ASSIGNEE_TEMPLATE = \
    Template('You are *assigned* to $author\'s pull request \"$title\" ($url), which is still awaiting approval.')  # noqa: E501
APPROVED_NOT_MERGED_TEMPLATE = \
    Template('Your pull request \"$title\" ($url) has been *approved*, but *not merged* yet.')
CHANGES_REQUESTED_TEMPLATE = \
    Template('Your pull request \"$title\" ($url) has had *changes requested* to it.')
GOODBYE_MSG = 'That\'s all for now!'


def greet(user):
    return HELLO_TEMPLATE.substitute(name=user)


def was_assigned(author, title, url, review_request=False):
    if review_request:
        msg = REQUESTED_REVIEWER_TEMPLATE
    else:
        msg = REQUESTED_ASSIGNEE_TEMPLATE
    return msg.substitute(author=author, title=title, url=url)


def review_made(title, url, has_reviewers_assigned=True, approved=False):
    if not has_reviewers_assigned:
        msg = NO_REVIEWERS_TEMPLATE.substitute(title=title, url=url)
    elif approved:
        msg = APPROVED_NOT_MERGED_TEMPLATE.substitute(title=title, url=url)
    else:
        msg = CHANGES_REQUESTED_TEMPLATE.substitute(title=title, url=url)

    return msg

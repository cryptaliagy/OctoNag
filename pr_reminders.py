#!/usr/bin/env python2.7

import os
import sys
import json
import requests
from github3 import enterprise_login
from string import Template


# Read Environment Variables
try:
    SLACK_API_TOKEN = os.environ['SLACK_API_TOKEN']
    GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']
except KeyError as error:
    sys.stderr.write('Please set the environment variable {0}'.format(error))
    sys.exit(1)


POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
LOOKUP_USER_URL = 'https://slack.com/api/users.lookupByEmail'

GITHUB_URL = 'http://code.corp.surveymonkey.com'
ORGANIZATION = 'wufoo'
GITHUB_REVIEW_LINK_TEMPLATE = \
    Template('https://code.corp.surveymonkey.com/api/v3/repos/wufoo/$repo/pulls/$number/reviews')

# Headers
slack_headers = { 'Authorization': 'Bearer ' + SLACK_API_TOKEN }
github_headers = { 'Authorization': 'Bearer ' + GITHUB_API_TOKEN }

REVIEWED_PR_TEMPLATE = Template('Hi there! This is a reminder that *your pull request* $repo/$number ($url) has been reviewed but *not approved*.')
REQUESTED_REVIEWER_TEMPLATE = Template('Hi there! This is a reminder that *you are a requested reviewer* on pull request $repo/$number ($url), which is still awaiting approval.')
NO_REVIEWERS_TEMPLATE = Template('Hi there! This is a reminder that *you haven\'t requested any reviewers* on pull request $repo/$number ($url).')


def fetch_repository_pulls(repository):
    pulls = []
    for pull in repository.pull_requests():
        if pull.state == 'open':
            pulls.append(pull)
    return pulls


def fetch_organization_pulls(organization_name):
    client = enterprise_login(
        token=GITHUB_API_TOKEN,
        url=GITHUB_URL
    )
    organization = client.organization(username=organization_name)

    pulls = []
    for repository in organization.repositories():
        pulls += fetch_repository_pulls(repository)

    return pulls


def lookup_user(name):
    email = name + '@surveymonkey.com'
    params = {
        'email': email
    }
    r = requests.get(LOOKUP_USER_URL, headers=slack_headers, params=params)
    if r.status_code == 200:
        response = json.loads(r.text)
        if response['ok']:
            return response['user']['id']
        else:
            print('Error looking up user by email: %s' % email)
            return None


def send_to_user(user_id, text):
    params = {
        'channel': user_id,
        'text': text
    }
    r = requests.post(POST_MESSAGE_URL, headers=slack_headers, params=params)


if __name__ == '__main__':
    pulls = fetch_organization_pulls('wufoo')
    for pull in pulls:

        user = pull.user.login
        url = pull.html_url
        number = pull.number
        repo = pull.repository[1]

        requested = [person['login'] for person in pull.requested_reviewers]
        requested_ids = [lookup_user(name) for name in requested]

        request_url = GITHUB_REVIEW_LINK_TEMPLATE.substitute(repo=repo, number=number)
        r = requests.get(request_url, headers=github_headers)
        reviews = json.loads(r.text)

        if len(reviews) >= 1:
            latest_review = reviews[len(reviews)-1]
            state = latest_review['state']
            if state != 'APPROVED':
                text = REQUESTED_REVIEWER_TEMPLATE.substitute(repo=repo, number=number, url=url)
                for user_id in requested_ids:
                    send_to_user(user_id, text)
                text = REVIEWED_PR_TEMPLATE.substitute(repo=repo, number=number, url=url)
                send_to_user(lookup_user(user), text)

        else:
            if len(requested_ids) > 0:
                text = REQUESTED_REVIEWER_TEMPLATE.substitute(repo=repo, number=number, url=url)
                for user_id in requested_ids:
                    send_to_user(user_id, text)
            else:
                text = NO_REVIEWERS_TEMPLATE.substitute(repo=repo, number=number, url=url)
                send_to_user(lookup_user(user), text)

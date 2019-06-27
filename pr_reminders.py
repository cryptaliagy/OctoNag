#!/usr/bin/env python2.7

import os
import sys
import json
import requests
from github3 import enterprise_login
from string import Template
from configuration import restrict, with_token, repositories, manually_resolve, organizations

github_url = 'http://code.corp.surveymonkey.com'
POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
LOOKUP_USER_URL = 'https://slack.com/api/users.lookupByEmail'

REVIEWED_PR_TEMPLATE = Template('Hi there! This is a reminder that *your pull request* $repo/$number ($url) has been reviewed but *not approved*.')
REQUESTED_REVIEWER_TEMPLATE = Template('Hi there! This is a reminder that *you are a requested reviewer* on pull request $repo/$number ($url), which is still awaiting approval.')
NO_REVIEWERS_TEMPLATE = Template('Hi there! This is a reminder that *you haven\'t requested any reviewers, or assigned someone* on pull request $repo/$number ($url).')
REQUESTED_ASSIGNEE_TEMPLATE = Template('Hi there! This is a reminder that the pull request $repo/$number ($url) that you have been *assigned* has not yet been reviewed.')
APPROVED_NOT_MERGED_TEMPLATE = Template('Hi there! This is a reminder that your pull request $repo/$number ($url) has been *approved*, but *not merged* yet.')
CHANGES_REQUESTED_TEMPLATE = Template('Hi there! This is a reminder that *your pull request* $repo/$number ($url) has had *changes requested* to it.')

user_cache = {}
message_recipients = []


def fetch_repository_pulls(repository):
    pulls = []
    for pull in repository.pull_requests():
        if pull.state == 'open':
            pulls.append(pull)
    return pulls

@with_token(service='Github')
@repositories
def fetch_organization_pulls(organization_name, _token, _repositories):
    client = enterprise_login(
        token=_token,
        url=github_url
    )
    organization = client.organization(username=organization_name)
    reviews_link = Template('{0}/api/v3/repos/{1}/$repo/pulls/$number/reviews'.format(github_url, organization_name))

    pulls = []
    if not _repositories:
        for repository in organization.repositories():
                pulls += fetch_repository_pulls(repository)
    else:
        for repository in _repositories:
            pulls += fetch_repository_pulls(client.repository(organization_name, repository))
    

    return (pulls, reviews_link)

@restrict('blacklist')
@restrict('whitelist')
@manually_resolve
def lookup_user(name):
    print ('Searching for %s...' % name)
    # Search only once for each user ID
    if name in user_cache:
        print('Found cached user %s with email %s' % (name, user_cache[name]['email']))
        return user_cache[name]['id']
    else:
        email = name + '@surveymonkey.com'

    email = 'nmaximo@surveymonkey.com'  # Temporary test override
    params = {
        'email': email
    }
    r = requests.get(LOOKUP_USER_URL, headers=get_header('Slack'), params=params)
    if r.status_code == 200:
        response = json.loads(r.text)
        if response['ok']:
            user_cache[name] = { 'id': response['user']['id'], 'email': email }
            user_cache[response['user']['id']] = { 'name': name, 'email': email }
            print('Slack user with email %s found' % email)
            return response['user']['id']
        else:
            print('Error looking up user by email: %s' % email)
            print('Error: %s' % response['error'])
            return None

def send_to_user(user_id, text):
    if user_id is None:
        return
    print("Sending message to %s..." % user_cache[user_id]['name'])
    params = {
        'channel': user_id,
        'text': text
    }
    r = requests.post(POST_MESSAGE_URL, headers=get_header('Slack'), params=params)

    message_recipients.append(user_cache[user_id]['name'])


def get_header(service):
    @with_token(service)
    def make_header(_token=None):
        return { 'Authorization': 'Bearer ' + _token }
    
    return make_header()


if __name__ == '__main__':
    for organization in organizations:
        pulls, review_link_template = fetch_organization_pulls(organization) # Token and repo list populated by decorators
        for pull in pulls:
            user = pull.user.login
            url = pull.html_url
            number = pull.number
            repo = pull.repository[1]
            user_id = lookup_user(user)

            requested = [person['login'] for person in pull.requested_reviewers]
            requested_ids = [lookup_user(name) for name in requested]

            assigned = [person['login'] for person in pull.assignees]
            assigned_ids = [lookup_user(name) for name in assigned]

            request_url = review_link_template.substitute(repo=repo, number=number)
            r = requests.get(request_url, headers=get_header('Github'))
            reviews = json.loads(r.text)

            fill_template = lambda template: template.substitute(repo=repo, number=number, url=url)
            
            if len(reviews) >= 1:
                state = \
                    reduce(lambda acc, nxt: acc if nxt['state'] not in ['CHANGES_REQUESTED', 'APPROVED'] else nxt['state'], reviews, reviews[0]['state'])

                if state == 'CHANGES_REQUESTED' and user_id is not None :
                    text = fill_template(CHANGES_REQUESTED_TEMPLATE)
                    send_to_user(user_id, text)
                elif state == 'APPROVED' and user_id is not None:
                    text = fill_template(APPROVED_NOT_MERGED_TEMPLATE)
                    send_to_user(lookup_user(user), text)
                elif state != 'APPROVED':
                    text = fill_template(REQUESTED_REVIEWER_TEMPLATE)
                    for user_id in requested_ids:
                        send_to_user(user_id, text)
                    text = fill_template(REVIEWED_PR_TEMPLATE)
                    send_to_user(lookup_user(user), text)
            else:
                if len(requested_ids) > 0:
                    text = fill_template(REQUESTED_REVIEWER_TEMPLATE)
                    for user_id in requested_ids:
                        send_to_user(user_id, text)
                
                if len(assigned_ids) > 0:
                    text = fill_template(REQUESTED_ASSIGNEE_TEMPLATE)
                    for user_id in assigned_ids:
                        send_to_user(user_id, text)

                if len(assigned_ids) == 0 and len(requested_ids) == 0:
                    text = fill_template(NO_REVIEWERS_TEMPLATE)
                    send_to_user(lookup_user(user), text)
    
    unique_nags = set(message_recipients)
    print('OctoNag has finished nagging for the day!')
    print('Sent %d nags to a total of %d people' % (len(message_recipients), len(unique_nags)))
    print('Nagged people: %s' % list(unique_nags))

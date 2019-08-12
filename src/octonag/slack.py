import requests
import json
from .configuration import restrict
from .configuration import get_header
from .configuration import manually_resolve
# from .configuration import debug

user_cache = {}
found = set()  # Used to silence lookups after the first time
POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
LOOKUP_USER_URL = 'https://slack.com/api/users.lookupByEmail'


@restrict('blacklist')
@restrict('whitelist')
@manually_resolve
def lookup_user(login, user_email='', name=''):
    if login in found:
        return user_cache[login]['id']
    print('Searching for %s...' % login)
    # Search only once for each user ID
    if login in user_cache:
        print('Found cached user %s with email %s' % (login, user_cache[login]['email']))
        found.add(login)
        return user_cache[login]['id']
    elif user_email != '':
        email = user_email
    else:
        email = login + '@surveymonkey.com'

    params = {
        'email': email
    }
    r = requests.get(LOOKUP_USER_URL, headers=get_header('Slack'), params=params)
    if r.status_code == 200:
        response = json.loads(r.text)
        if response['ok']:
            if name:
                logged_name = name
            else:
                logged_name = response['user']['profile']['display_name']
            user_cache[login] = {'id': response['user']['id'], 'email': email, 'name': logged_name}
            user_cache[response['user']['id']] = {
                'login': login,
                'email': email,
                'name': logged_name
            }
            print('Slack user with email %s found' % email)
            return response['user']['id']
        else:
            print('Error looking up user by email: %s' % email)
            print('Error: %s' % response['error'])
            return None


# @debug
def msg_user(user_id, text):
    if user_id is None:
        return

    if user_id in user_cache:
        print("Sending message to %s..." % user_cache[user_id]['login'])
    else:
        print('debug...')
    params = {
        'channel': user_id,
        'text': text
    }
    requests.post(POST_MESSAGE_URL, headers=get_header('Slack'), params=params)


def get_name_from_id(uid):
    name = user_cache[uid]['name']
    if name:
        return name
    return user_cache[uid]['login']

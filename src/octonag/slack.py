import slack
import logging
from .configuration import restrict
from .configuration import get_slack_token
from .configuration import manually_resolve
from .configuration import default_email_domain
# from .configuration import debug

user_cache = {}
found = set()  # Used to silence lookups after the first time
client = slack.WebClient(token=get_slack_token())


@restrict('blacklist')
@restrict('whitelist')
@manually_resolve
def lookup_user(login, user_email='', name=''):
    logging.debug('Attempting to look up user with login %s, email %s, name %s',
                  login, user_email, name)
    if user_email is None:
        logging.debug('No email passed to function')
        return None
    if login in found:
        logging.debug('User in cache')
        return user_cache[login]['id']
    logging.info('Searching for %s...' % login)
    # Search only once for each user ID
    if login in user_cache:
        logging.info('Found cached user %s with email %s' % (login, user_cache[login]['email']))
        found.add(login)
        return user_cache[login]['id']
    elif user_email != '':
        email = user_email
    elif default_email_domain:
        email = login + default_email_domain

    try:
        r = client.users_lookupByEmail(
            email=email
        )
    except Exception as e:
        logging.error('An error occurred when doing the lookup for %s', email)
        logging.error(e)
        return None
    if r.status_code == 200:
        response = r.data
        if response['ok']:
            if name:
                logging.debug('Using passed name instead of found name')
                logged_name = name
            else:
                logging.debug('No name passed to function, using one from response')
                logged_name = response['user']['profile']['display_name']
            logging.debug('Adding user to cache')
            user_cache[login] = {'id': response['user']['id'], 'email': email, 'name': logged_name}
            user_cache[response['user']['id']] = {
                'login': login,
                'email': email,
                'name': logged_name
            }
            logging.info('Slack user with email %s found' % email)
            return response['user']['id']
        else:
            logging.warning('Error looking up user by email: %s' % email)
            logging.warning('Error: %s' % response['error'])
            logging.warning('Returning None to skip user')
            return None


# @debug
def msg_user(user_id, text):
    if user_id is None:
        return

    if user_id in user_cache:
        logging.info('Sending message to %s...' % user_cache[user_id]['login'])
    else:
        logging.debug('Sending message to debug user...')
    response = client.chat_postMessage(
        channel=user_id,
        text=text
    )
    if response.status_code == 200:
        logging.info('Message sent successfully')
    else:
        logging.error('Message was not sent successfully')


def get_name_from_id(uid):
    name = user_cache[uid]['name']
    if name:
        return name
    return user_cache[uid]['login']

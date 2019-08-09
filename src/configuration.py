import sys
import os
from yaml import load, Loader
from functools import wraps

def get_config_from_file(config_file='conf/config.yaml'):
    """
    Grabs the configuration from YAML file
    """
    with open(config_file, 'r') as f:
        try:
            config = load(f.read(), Loader=Loader)
        except Exception as e:
            sys.stderr.write(e)
            sys.stderr.write("Error reading configuration file {}".format(config_file))
            sys.exit(1)
    return config


class _config:
    def __init__(self):
        configs = get_config_from_file()
        self.github_token = os.getenv('GITHUB_API_TOKEN')
        self.slack_token = os.getenv('SLACK_API_TOKEN')
        self.jira_user = os.getenv('JIRA_USER')
        self.jira_pass = os.getenv('JIRA_PASS')

        if self.slack_token is None \
            or self.github_token is None:
            sys.stderr.write('Please ensure that the github token and slack token are defined in the config file')
            sys.exit(1)

        self.map_users = configs['manually_resolve_users']
        self.repositories = configs['repositories']
        self.whitelist = configs['whitelist'] and {*configs['whitelist']}
        self.blacklist = configs['blacklist'] and {*configs['blacklist']}
        self.use_jira = configs['use_jira']


Configuration = _config()
organizations = Configuration.repositories.keys()
github_url = 'https://code.corp.surveymonkey.com'
github_graphql = f'{github_url}/api/graphql'
blocked = set()
mapped = set()

def repository_generator(repos=None):
    if repos is None:
        repositories = Configuration.repositories
    else:
        repositories = repos
    
    for owner in repositories:
        for repository in repositories[owner]:
            yield owner, repository


def restrict(list_type):
    def restricting_decorator(func):
        @wraps(func)
        def wrapper(name, *args, **kwargs):
            if list_type == 'blacklist':
                collection = Configuration.blacklist
            elif list_type == 'whitelist':
                collection = Configuration.whitelist
            else:
                collection = None

            if name in blocked:
                return None  # Block quietly after first verbose block
            
            if collection and ((list_type == 'whitelist') ^ (name in collection)):
                print('User %s %s in %s, blocking lookup' % (name, 'not' if list_type=='whitelist' else '', list_type))
                blocked.add(name)
                return None

            return func(name, *args, **kwargs)

        return wrapper
    return restricting_decorator

def with_credentials(service='Jira'):
    def use_credentials(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if service == 'Jira':
                usr = Configuration.jira_user
                pwd = Configuration.jira_pass
            new_kwargs = kwargs.copy()
            new_kwargs['_usr'] = usr
            new_kwargs['_pwd'] = pwd
            return func(*args, **new_kwargs)
        return wrapper
    return use_credentials

def with_token(service='Github'):
    def use_token(func):
        @wraps(func)
        def wrapper(*args, **kwargs): 
            if service == 'Github':
                token = Configuration.github_token
            else:
                token = Configuration.slack_token
            new_kwargs = kwargs.copy()
            new_kwargs['_token'] = token
            return func(*args, **new_kwargs)
        return wrapper
    return use_token

def repositories(func):
    @wraps(func)
    def wrapper(organization, *args, **kwargs):
        new_kwargs = kwargs.copy()
        new_kwargs['_repositories'] = Configuration.repositories[organization]
        return func(organization, *args, **new_kwargs)
    return wrapper
    
def manually_resolve(func):
    @wraps(func)
    def wrapper(name, *args, **kwargs):
        if name in mapped:
            return func(Configuration.map_users[name], *args, **kwargs)
            
        if Configuration.map_users and name in Configuration.map_users:
            print('%s in manual mapping configuration, doing lookup on %s' % (name, Configuration.map_users[name]))
            mapped.add(name)
            return func(Configuration.map_users[name], *args, **kwargs)
        return func(name, *args, **kwargs)
    return wrapper


def get_header(service):
    @with_token(service)
    def make_header(_token=None):
        return { 'Authorization': 'Bearer ' + _token }
    
    return make_header()


def debug(func):
    @wraps(func)
    def wrapper(uid, *args, **kwargs):
        return func('UJJJKJZEF', *args, **kwargs)
    return wrapper
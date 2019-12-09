import pytest
from unittest.mock import patch
from octonag.configuration import get_config_from_file
from octonag.configuration import repository_generator
from octonag.configuration import with_credentials
from octonag.configuration import with_token
from octonag.configuration import Configuration
from octonag.configuration import _config
from octonag.configuration import restrict
from octonag.configuration import repositories
from octonag.configuration import manually_resolve
from octonag.configuration import get_header
from octonag.configuration import get_slack_token
from octonag.configuration import debug


repository = {
    'org': ['repo']
}


def make_config(use_jira=False):
    config = {
        'use_jira': use_jira,
        'manually_resolve_users': None,
        'repositories': None,
        'whitelist': None,
        'blacklist': None,
        'ignore_no_assigned': None,
        'ignore_no_requested': None,
        'send_greeting': None,
        'default_email_domain': None
    }
    return config


@pytest.mark.unit
def test_repository_generator():
    repos = repository_generator(repository)

    assert next(repos) == ('org', 'repo')

    Configuration.repositories = repository

    repos = repository_generator()

    assert next(repos) == ('org', 'repo')


@pytest.mark.unit
@patch('octonag.configuration.load')
@patch('sys.exit')
def test_config_exception(mock_exit, mock_load):
    mock_load.side_effect = Exception
    mock_exit.return_value = None
    try:
        get_config_from_file()
    except Exception as e:
        assert type(e) == UnboundLocalError

    mock_exit.assert_called_with(1)


@pytest.mark.unit
@patch('os.getenv')
@patch('octonag.configuration.get_config_from_file')
def test_use_jira(mock_config, mock_env):
    mock_config.return_value = make_config(use_jira=True)
    mock_env.side_effect = ['1234', '1234', 'user', 'pass', None]

    conf = _config()

    assert conf.jira_user == 'user'
    assert conf.jira_pass == 'pass'


@pytest.mark.unit
@pytest.mark.parametrize('token_vals', [
    ([None, 'some']),
    (['some', None]),
    ([None, None])
])
@patch('sys.exit')
@patch('os.getenv')
@patch('octonag.configuration.get_config_from_file')
def test_no_token(mock_config, mock_env, mock_exit, token_vals):
    mock_config.return_value = make_config()
    mock_env.side_effect = token_vals + [None]
    mock_exit.return_value = None

    conf = _config()

    assert conf.github_token == token_vals[0]
    assert conf.slack_token == token_vals[1]

    mock_exit.assert_called_with(1)


@pytest.mark.unit
def test_with_credentials():
    Configuration.jira_pass = '1234'
    Configuration.jira_user = 'user'
    @with_credentials()
    def return_credentials(_usr=None, _pwd=None):
        return _usr, _pwd

    usr, pwd = return_credentials()

    assert usr == 'user'
    assert pwd == '1234'


@pytest.mark.unit
def test_with_token():
    Configuration.github_token = '12345'
    Configuration.slack_token = 'abcde'

    def return_token(_token=None):
        return _token

    return_github_token = with_token('Github')(return_token)
    assert return_github_token() == '12345'

    return_slack_token = with_token('Slack')(return_token)
    assert return_slack_token() == 'abcde'


@pytest.mark.unit
def test_restrict():
    Configuration.whitelist = {'1234'}
    Configuration.blacklist = {'4321'}

    def return_name(name):
        return name

    whitelist = restrict('whitelist')(return_name)
    blacklist = restrict('blacklist')(return_name)
    invalid = restrict('invalid')(return_name)

    assert invalid('abcde') == 'abcde'
    assert whitelist('1234') == '1234'
    assert whitelist('4321') is None
    assert blacklist('1234') == '1234'
    assert blacklist('4321') is None


@pytest.mark.unit
def test_repositories():
    Configuration.repositories = repository

    @repositories
    def return_repositories(org='org', _repositories=None):
        return _repositories

    assert return_repositories('org') == ['repo']


@pytest.mark.unit
def test_manually_resolve():
    Configuration.map_users = {
        'abcde': '1234'
    }

    @manually_resolve
    def return_username(name):
        return name

    resolved_name = return_username('abcde')
    resolved_name = return_username('abcde')
    assert resolved_name == '1234'

    resolved_name = return_username('not_in_map_users')
    assert resolved_name == 'not_in_map_users'


@pytest.mark.unit
def test_get_header():
    Configuration.github_token = '1234'
    Configuration.slack_token = '1234'

    github_header = get_header('Github')
    slack_header = get_header('Slack')

    assert github_header == {'Authorization': 'Bearer 1234'}
    assert slack_header == {'Authorization': 'Bearer 1234'}


@pytest.mark.unit
def test_get_slack_token():
    Configuration.slack_token = '1234'

    assert get_slack_token() == '1234'


@pytest.mark.unit
def test_debug():
    Configuration.debug_uid = '1234'

    @debug
    def get_uid(uid):
        return uid

    uid = get_uid('abcde')

    assert uid == '1234'

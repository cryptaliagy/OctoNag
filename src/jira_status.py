from configuration import with_credentials
from jira import JIRA
from jira.exception import JIRAError

jira_url = 'https://jira.surveymonkey.com'


@with_credentials(service='Jira')
def in_review(issue_id, _usr, _pwd):
    if _usr is None or _pwd is None:
        print('Jira username or password unset.')
        return None
    jira = None
    try:
        jira = JIRA(
            jira_url,
            auth=(_usr, _pwd)
        )
        issue = jira.issue(issue_id)
        if str(issue.fields.status) == 'Review':
            return True
        else:
            return False
    except JIRAError:
        if jira is None:
            print('Could not connect to Jira.')
        else:
            print('Could not check Jira ticket status on %s.' % issue_id)
        return None

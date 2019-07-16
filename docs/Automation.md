# Setting Up TeamCity

If you would like to set up automation through TeamCity, there are two ways: Using the TeamCity project already in place for other teams, or setting up your own. When using the automation that is already in place, you will still have the ability to customize your notification schedule.

1. [Using Existing Automation](#using-existing-automation)
   1. [Using Default Notifications](#using-default-notifications)
   1. [Setting up additional notifications](#setting-up-additional-notifications)
1. [Setting Up New Automation Through TeamCity](#setting-up-new-automation-through-teamcity)

-----
## Using Existing Automation

### Using Default Notifications
By default, you can use the notification times that are currently in place. By using a specific name for your configuration branch, TeamCity will find and build the branches. The default time is Monday-Friday at 8 am.

Branch names will specify what timezone to use. The currently supported ones are outlined below:
- est-*
- pst-*

As an example, the EnterpriseWeb team has a configuration branch and would like to be notified every morning at 8 am EST, and therefore the name of the branch for the EnterpriseWeb team is est-enterpriseweb


### Setting Up Additional Notifications
If the default time for OctoNag notifications does not work for your team, or you would like more than one notification a day, you may configure your own notifications in the [OctoNag TeamCity Project](https://teamcity.corp.surveymonkey.com/viewType.html?buildTypeId=OctoNag_OctoNagBuildConfiguration). This is usually done as a Cron job and can be done as follows:

1. Go to the [OctoNag TeamCity Project Triggers](https://teamcity.corp.surveymonkey.com/admin/editTriggers.html?id=buildType:OctoNag_OctoNagBuildConfiguration) page
1. Click 'Add new trigger'
1. Select 'Schedule Trigger'
1. Configure the times you would like to be notified
1. Unselect 'Trigger only if there are pending changes' under the 'VCS Changes' tab
1. Click on 'Advanced Options'
1. Select 'Clean all files in checkout directory before build'
1. Under 'Edit Branch Filter', add in the following, replacing my_branch_name with your branch's name:
    ```
    +:my_branch_name
    ```
-------

## Setting Up New Automation Through TeamCity
If you would like to fork the repository and set up notifications from your fork, ensure some of the following things before you start:

1. You have a Github Personal Access Token
1. You have a Slack Personal Access Token
1. You can create new projects on TeamCity

It would also be beneficial to familiarize yourself with TeamCity and the Make commands that come with OctoNag

To set up OctoNag in a new TeamCity project, do the following:

1. Create & name your new project
1. Under 'General Settings', select 'enable hanging builds detection'
1. Under 'Version Control Settings' add your GitHub repository as a VCS root
    1. Under 'Checkout Options', in the VCS Checkout Mode field, select 'Automatically on agent (if supported by VCS roots)'
    1. Under 'Checkout Options', select 'Clean all files in the checkout directory before the build'
1. Under 'Build Steps', add in the steps you would like to use.
1. Under 'Triggers', add in the triggers that you would like. If you need help, check the [Setting up additional notifications](#setting-up-additional-notifications) section

> *Note*: The default OctoNag project uses `make build`, `make run`, and `make teardown` as the commandline scripts to build the OctoNag. It uses those commands as separate build steps, but it is possible to use simply `make activate` as a singular build step. Whether that is advisable or not is left to the discretion of the reader.
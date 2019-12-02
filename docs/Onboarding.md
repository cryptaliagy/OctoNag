# Tutorial – How to use the OctoNag

## Table of Contents
1. [Getting Started – Why should I care?](#getting-started-–-why-should-i-care)
1. [What am I going to need?](#what-am-i-going-to-need?)
1. [Writing your configuration file](#writing-your-configuration-file)
    1. [Manually resolving users](#manually-resolving-users)
1. [Personal Access Tokens](#personal-access-tokens)
    1. [Github Token](#github-token)
    1. [Slack Token](#slack-token)


## Getting Started – Why should I care?
The OctoNag is a script to send reminders of pull requests to relevant developers. Whereas Github's notification system will often saturate developers and contributors with emails, the OctoNag sends a digest of actionable messages to developers whenver it is run.

Many teams will currently configure GitHub to notify some channel whenever a pull request is opened, but it often leads to the bystander effect. By personally messaging developers, the OctoNag offers an innovative approach to reminders, helping them stay on top of their tasks and remain accountable to their team.

## What am I going to need?

Before starting up, make sure you know what repositories you would like notifications for, and which users you would like to set up notifications for.

For this example, I'm going to assume the following things:

1. My team is comprised of users with the username "nmaximo", "auser", "onag", and "octocat"
1. We work on the repositories 'nmaximo/octonag', 'nmaximo/myproject', and 'auser/publicrepo'

Now that we know that, it's time to configure our OctoNag! Create a new branch and name it after your team, and we can get started. For this tutorial, our team name will be `octonag-team`

## Installation guide

> ### Note: It is highly recommended to use virtualenvwrapper or virtualenv to limit conflicts with other package requirements

To install the OctoNag, first clone the repository:

```bash
    git clone git@code.corp.surveymonkey.com:nmaximo/OctoNag.git
```

Next, install the package:

```bash
    # In the directory you cloned the repository into
    pip install .
```

If you are wanting to develop and contribute to the OctoNag, you need to also install the pre-commit hooks, and you probably want to install the package so that changes you write are included whenever you run the octonag again. A script is included for this and can be run as such:

```bash
    # In the directory you cloned the repository into
    ./install
```

## Writing your configuration file

First, I must open up my configuration file ([conf/config.yaml](../conf/config.yaml)). Since I have just started a new project, I'm working on a branch that I started from the latest master, so I should see this blank configuration file:

```yaml
# Entries are of the form
# Organization:
#   - Repository
repositories:

# Restrict notifications to only be given to these Github users, or leave empty to notify any users
whitelist:

# Prevent these users from being messaged. Overrides whitelist
blacklist:

# For anyone whose Github username does not match their work email
manually_resolve_users:

use_jira: False
```

Since my team is working on 'nmaximo/octonag', 'nmaximo/myproject', and 'auser/publicrepo', I need to write my repository list like this:

```yaml
repositories:
  nmaximo:
    - octonag
    - myproject
  auser:
    - publicrepo
```

Now, to configure my teammates on the whitelist:

```yaml
whitelist:
  - nmaximo
  - auser
  - onag
  - octocat
```

### Manually resolving users
Now, unfortunately, one of my teammates decided to customize their Github username! Whereas `nmaximo`, `auser`, and `onag` all have their work email in slack as `nmaximo@company.com`, `auser@company.com`, and `onag@company.com`, `octocat`'s email is actually `ocat@company.com`!

> *Note*: If there is a name mismatch between Github usernames and the email used for Slack, there are two ways of resolving the conflict and making sure your developer still gets the right notifications. The first is to ensure that their work email is set to public on their profile. The second is to manually resolve their usename through the configuration file. The former method is preferred if possible!

Unfortunately `octocat` cannot set their email to public, so we **must** add `octocat` to the configuration's "`manually_resolve_users`" section.

```yaml
manually_resolve_users:
  octocat: ocat
```

This will tell the OctoNag that whenever the Github username "`octocat`" is found, try to do a lookup with `ocat@company.com` instead of `octocat@company.com`.

Now that we have our team and our repositories configured, our `conf/config.yaml` file should look like this:

```yaml
# Entries are of the form
# Organization:
#   - Repository
repositories:
  nmaximo:
    - octonag
    - myproject
  auser:
    - publicrepo

# Restrict notifications to only be given to these Github users, or leave empty to notify any users
whitelist:
  - nmaximo
  - auser
  - onag
  - octocat

# Prevent these users from being messaged. Overrides whitelist
blacklist:

# For anyone whose Github username does not match their work email
manually_resolve_users:
  octocat: ocat


use_jira: False
```


## Personal Access Tokens

Since the OctoNag integrates with Github and Slack, it is necessary to install it as an app in the workspace on Slack and to get the appropriate authorization key from Github. This is necessary if creating new automation or for development. If you would like to use existing automation, and do not want to develop for the OctoNag, feel free to skip this.

### Github Token
Read [this article](https://help.github.com/en/articles/creating-a-personal-access-token-for-the-command-line) to generate your Github token. The permissions necessary are `repo` and `user:email`. Once you have your token generated, add it to the environment variable `GITHUB_API_TOKEN`

### Slack Token
Read [this article](https://api.slack.com/start/overview#creating) to create and set up your Slack app and generate your token. The permissions necessary are `chat:write:bot`, `users:read`, `users:read.email`, and `users.profile:read`. Once you have your token generated, add it to the environment variable `SLACK_API_TOKEN`

### (Optional) Jira User and Password
By enabling the setting `use_jira` in your config file and having the variables `JIRA_USER` and `JIRA_PASS` set, the OctoNag will attempt to find the Jira tickets associated with the PRs that it would typically notify users about (this works for PRs with titles formatted like `JIRA-1234: Details of PR`). If a PR is matched to a Jira ticket, notifications will only be sent if the ticket is in the `Review` state. If either of `JIRA_USER` or `JIRA_PASSWORD` are unset, then the Octonag will not connect to Jira and notifications will be sent for all appropriate PRs. This is useful when the QA process for your team occurs before the ticket gets merged, allowing developers to stay nag-free while the tickets are not yet ready to be merged.

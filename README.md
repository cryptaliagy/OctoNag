# OctoNag Bot

THIS PROJECT IS ARCHIVED AND NO LONGER MAINTAINED. I am currently working on a re-write of it in Rust, you can find it here -> https://github.com/taliamax/octo_nag

## Build Status
![Pytest](https://github.com/taliamax/OctoNag/workflows/Pytest/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/taliamax/OctoNag/badge.svg?branch=develop)](https://coveralls.io/github/taliamax/OctoNag?branch=develop)

## Quickjump
1. [Onboarding](#onboarding)
1. [Configuration](#configuration)
1. [Setup Locally Using Virtual Environment](#setup-locally-using-virtual-environment)
1. [Setup Locally Using Docker](#setup-locally-using-docker)
1. [Setting Up Automation](#setting-up-automation)

## Onboarding

For a more detailed guide on how to start up and configure your OctoNag instance, look at the [onboarding docs](docs/Onboarding.md)


## Configuration
1. Make sure that SLACK_API_TOKEN and GITHUB_API_TOKEN are set as environment variables
1. (Optional) set JIRA_USER and JIRA_PASS as environment variables to mute notifications for pull requests that can be linked to Jira tickets in states other than `REVIEW`.
1. Add organizations & repositories to watch onto your conf/config.yaml file
1. Add your team members to the whitelist. It is highly recommended that you add your teammates to the whitelist to make sure that if anyone else is also contributing to the repo, they will not get unexpected nags.
1. If necessary (i.e. when members are on PTO/out sick/should not be nagged), add team members to the blacklist

## Setup Locally Using Virtual Environment
*Note*: This setup guide assumes you have [pip](https://pip.pypa.io/en/stable/installing/), [virtualenv](https://virtualenv.pypa.io/en/stable/installation/), and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html#basic-installation) installed, and are working on a Linux or Mac terminal. As a reminder, the OctoNag runs on Python 3.

1. Create a new virtual environment:
```bash
    # In the octonag directory
    mkvirtualenv octonag -a .
```
2. Activate the virtual environment:
```bash
    workon octonag
```
3. Install the OctoNag
```bash
    ./install    # Installs the octonag & the pre-commit hooks
```
You can now run the OctoNag by using:
```bash
    octonag
```

The OctoNag has pre-commit hooks enabled. This is to ensure that all code that is committed meets a minimum threshold of quality, so that all problems can be caught as early as possible. Currently, this means running `flake8`.

## Setup Locally Using Docker
*Note*: Requires Docker for [Mac](https://docs.docker.com/docker-for-mac/install/) or [Windows](https://docs.docker.com/toolbox/toolbox_install_windows/) or [Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)

The OctoNag comes with the following handy make commands for Docker usage. They can be seen below:
```bash
make build      # Builds the image
make run        # Runs the OctoNag
make test       # Runs the OctoNag tests
make teardown   # Deletes the image
make rebuild    # Tears down, then builds the image
make activate   # Tears down image if existing, builds it, runs, then cleans up
```

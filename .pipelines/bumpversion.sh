#!/bin/bash

# Release Automation
#   - Bump Version
#   - Create Tag
#

# Set git config
git config --global user.email $GIT_EMAIL
git config --global user.name $GIT_NAME
git config --global push.default simple

# Clone Repo
git clone https://$GIT_USERNAME:$GIT_PASSWORD@$AMAZONIA_REPO amazonia-repo && echo "!! GIT CLONE"
cd amazonia-repo

## Merge to Master
git checkout integration && echo "!! GIT CHECKOUT INTEGRATION"
git checkout master && echo "!! GIT CHECKOUT MASTER"
git merge integration --no-edit && echo "!! GIT MERGE INTEGRATION"

## Bump Integration Version
git checkout integration && echo "!! GIT CHECKOUT INTEGRATION"
bumpversion $BUMPVERSION_TYPE --list --verbose --tag && echo "!! BUMPVERSION"

## Push Both Commits and Tags
git push origin --all && echo "!! GIT PUSH --ALL"
git push origin --tags && echo "!! GIT PUSH --TAGS"
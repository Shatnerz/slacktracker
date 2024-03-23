#!/usr/bin/env bash

export PYENV_ROOT="$HOME/.pyenv"
. ${PYENV_ROOT}/versions/slacktrack/bin/activate

 DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
 cd $DIR

# Source SLACK_TOKEN
set -a
. secrets
set +a

mkdir -p logs
LOGS="logs/log"

date >>  $LOGS 2>&1
python track.py >>  $LOGS 2>&1
echo "" >>  $LOGS 2>&1
echo "" >>  $LOGS 2>&1

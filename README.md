# Slack Tracker

Watch changes to Slack Users.

Attempt to display data in an interesting manner.


## Scripts

- `track.py` - pull all users, separate between bots and humans, and git commit
    in order to make tracking changes easier

- `attrition.py` - Plot departures per week based on deleted human users


## Cron

Run once a day at midnight

```cron
0 0 * * *    /home/USER/dev/slack/track/run.sh
```

Requires setting `secrets` with

```
SLACK_TOKEN="YOUR-SLACK-TOKEN"
```


## Notes

Use `pyenv` and python 3.11.0 for convenience.

```bash
pyenv virtualenv 3.11.0 slacktrack
pip install slack_sdk
pip install GitPython

pip install pandas
pip install matplotlib
pip install PyQt5
```

"users:read" permission scope is required

Can potentially use
```python
'updated': 1633752686,
```
To determine date of departure for people

```python
'deleted': True,
```


## Running

```bash
export SLACK_TOKEN=""
python track.py
```

The token must have "users:read" permission scope
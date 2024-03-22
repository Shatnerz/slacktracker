# Slack Tracker

Watch changes to Slack Users.

Attempt to display data in an interesting manner.


## Notes

Use `pyenv` and python 3.11.0 for convenience.

```bash
pyenv virtualenv 3.11.0 slacktrack
pip install slack_sdk
pip install GitPython
```

Use `ipython3`

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
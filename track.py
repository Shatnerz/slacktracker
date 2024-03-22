import csv
import json
import os
import time
from datetime import datetime, UTC
from operator import itemgetter
from pathlib import Path

from git import Repo, InvalidGitRepositoryError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_users(client, cursor=None):
    """Return a list of users and the next_cursor in case of pagination"""
    while True:
        try:
            # Limit is an attempt to cutdown on random errors such as
            # Error fetching users: IncompleteRead(1420552 bytes read, 403251 more expected)
            # See: https://api.slack.com/methods/users.list
            # > We recommend no more than 200 results at a time.
            result = client.users_list(cursor=cursor, limit=1000)
            users = result['members']
            next_cursor = result.get("response_metadata", {}).get("next_cursor")
            return {
                "users": users,
                "next_cursor": next_cursor,
            }
        except Exception as e:
            print(f"Error fetching users: {e}")
            time.sleep(5)


def get_all_users(token):
    """Return a list of all users and associated data
    
    Automatically handle pagination."""
    try:
        client = WebClient(token=token)
        users = []

        run = True
        cursor = None
        while run:
            print("***")
            user_batch, cursor = itemgetter('users', 'next_cursor')(get_users(client, cursor))
            users.extend(user_batch)
            if not cursor:
                run = False

        return users

    except SlackApiError as e:
        print(f"Error fetching all users: {e}")


def save_raw_json_data(data, filename):
    """Save json data in raw/"""
    path = Path(__file__).parent / "raw" / filename
    if not os.path.exists(path):
        os.makedirs(path.parent)
    with open(path, 'w') as file:
        json.dump(data, file, indent=2)


def load_raw_json_data(filename):
    """Convenience function so I don't have to keep making API calls"""
    path = Path(__file__).parent / "raw" / filename
    with open(path, 'r') as file:
        return json.load(file)


def get_repo(path):
    """Get the git repo at the given path.
    
    If no repo exists create one.
    Switch to master branch.
    If master does not exist, create master branch.
    Creates an initial commit when creating master branch.
    """
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        repo = Repo(path=path)
        new_repo = False
    except InvalidGitRepositoryError:
        repo = Repo.init(path=path)
        new_repo = True

    config_writer = repo.config_writer()
    config_writer.set_value("user", "name", "Slack Tracker").release()
    config_writer.set_value("user", "email", "slacktrack@example.com").release()

    if new_repo is True:
        repo.index.commit("initial commit")
    
    if "master" in repo.heads:
        master = repo.heads.master
    else:
        master = repo.create_head("master")
    
    repo.head.reference = master
    repo.head.reset(index=True, working_tree=True)

    return repo

def commit_changes(repo):
    """Add all untracked files and commit.
    
    Commit message will just be a human readable UTC
    timestamp.
    """
    repo.git.add(A=True)
    utcnow = datetime.now(UTC)
    human_time = utcnow.strftime("%Y-%m-%d %H:%M:%S")
    repo.index.commit(f"Automated commit: {human_time}")


def process_data(all_users, path):
    """Process raw user data into CSVs in data/ and then commit changes.
    
    Assume that all_users is sorted.
    """
    bots = {
        "active": [],
        "deleted": [],
    }
    humans = {
        "active": [],
        "deleted": [],
    }
    for user in all_users:
        if user.get("is_bot") is True:
            category = bots
        else:
            category = humans

        if user.get("deleted") is True:
            category["deleted"].append(user)
        else:
            category["active"].append(user)

    if not os.path.exists(path):
        os.makedirs(path)

    process_group(humans, 'humans', path)
    process_group(bots, 'bots', path)

    # Git commit to track changes
    raw_repo = get_repo(path)
    commit_changes(raw_repo)
    
    
def process_group(group, prefix, path):
    """Process a dict of {"active": [], "deleted": [] } in CSVs"""
    active_path = path / f"{prefix}_active.csv"
    deleted_path = path / f"{prefix}_deleted.csv"
    
    active_fields = ["name", "id", "real_name", "title", "team_id"]
    deleted_fields = ["name", "id", "real_name", "title", "team_id", "updated_epoch", "updated_human"]

    def get_data(user):
        updated = user.get("updated")
        human_updated = datetime.fromtimestamp(updated).strftime("%Y-%m-%d %H:%M:%S")
        return [
            user.get("name"),
            user.get("id"),
            user.get("real_name"),
            user.get("profile", {}).get("title"),
            user.get("id"),
            updated,
            human_updated,
        ]

    with open(active_path, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(active_fields)
        rows = [get_data(x)[:-2] for x in group["active"]]
        csvwriter.writerows(rows)
        
    with open(deleted_path, "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(deleted_fields)
        rows = [get_data(x) for x in group["deleted"]]
        csvwriter.writerows(rows)


if __name__ == "__main__":
    SLACK_TOKEN = os.environ["SLACK_TOKEN"]
    all_users = get_all_users(SLACK_TOKEN)
    # all_users = load_raw_json_data("all_users.json")

    # Sort to keep order deterministic and make tracking changes easy
    all_users.sort(key=lambda user: user["name"])

    save_raw_json_data(all_users, "all_users.json")

    raw_path = Path(__file__).parent / "raw"
    data_path = Path(__file__).parent / "data"

    # Commit changes to raw data in raw/
    raw_repo = get_repo(raw_path)
    commit_changes(raw_repo)

    # Process into CSVs and commit in data/
    process_data(all_users, data_path)

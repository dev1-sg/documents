import os
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

GITLAB_PROJECT = os.getenv("GITLAB_PROJECT", "dev1-sg/public/bash-scripts")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
TZ = ZoneInfo("Asia/Singapore")

def singapore_time(dt_str):
    if not dt_str:
        return None
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt.astimezone(TZ).replace(microsecond=0).isoformat()

def fetch_gitlab_snippets(project):
    gitlab_project = urllib.parse.quote(project, safe='')
    url = f"https://gitlab.com/api/v4/projects/{gitlab_project}/snippets"
    headers = {
        "Accept": "application/json",
        "PRIVATE-TOKEN": GITLAB_TOKEN
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.load(response)

def lambda_handler(event, context):
    snippets = fetch_gitlab_snippets(GITLAB_PROJECT)
    data = []
    for snippet in snippets:
        updated_at = singapore_time(snippet.get("updated_at"))
        data.append({
            "name": snippet.get("title"),
            "id": snippet.get("id"),
            "raw_url": snippet.get("raw_url"),
            "updated_at": updated_at
        })

    return {
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({f"gitlab-dev1-sg-snippets": data}, indent=2)
    }

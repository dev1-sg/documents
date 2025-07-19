import os
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

GITHUB_ORG = os.getenv("GITHUB_ORG", "dev1-sg")
TZ = ZoneInfo("Asia/Singapore")

def singapore_time(dt_str):
    if not dt_str:
        return None
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt.astimezone(TZ).replace(microsecond=0).isoformat()

def fetch_github_repos(org, per_page=100):
    url = f"https://api.github.com/orgs/{org}/repos?type=public&per_page={per_page}"
    headers = {
        "User-Agent": "lambda-client",
        "Accept": "application/vnd.github.mercy-preview+json"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.load(response)

def lambda_handler(event, context):
    repos = fetch_github_repos(GITHUB_ORG)
    data = []
    for repo in repos:
        pushed_at = singapore_time(repo.get("pushed_at"))
        data.append({
            "name": repo.get("name"),
            "description": repo.get("description"),
            "language": repo.get("language"),
            "topics": repo.get("topics", []),
            "url": repo.get("html_url"),
            "clone_url": repo.get("clone_url"),
            "last_push": pushed_at
        })

    return {
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({f"github-{GITHUB_ORG}-repos": data}, indent=2)
    }

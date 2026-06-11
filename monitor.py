import os
import hashlib
import requests

URL = "https://steamdb.info/app/3678970/history/"

WEBHOOK = os.environ["DISCORD_WEBHOOK"]
TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]

headers = {
    "User-Agent": "Mozilla/5.0"
}

# SteamDB取得
html = requests.get(URL, headers=headers).text
new_hash = hashlib.sha256(html.encode()).hexdigest()

# GitHub Issueを状態保存に使う
issue_title = "STEAMDB_HASH"

api_headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# 既存Issue検索
r = requests.get(
    f"https://api.github.com/repos/{REPO}/issues",
    headers=api_headers,
    params={"state": "open"}
)

issues = r.json()

issue = None
for i in issues:
    if i["title"] == issue_title:
        issue = i
        break

old_hash = ""

if issue:
    old_hash = issue["body"]

if old_hash != new_hash:

    requests.post(
        WEBHOOK,
        json={
            "content": f"🔔 Task Bar Hero SteamDB 更新！\n{URL}"
        }
    )

    if issue:
        requests.patch(
            issue["url"],
            headers=api_headers,
            json={"body": new_hash}
        )
    else:
        requests.post(
            f"https://api.github.com/repos/{REPO}/issues",
            headers=api_headers,
            json={
                "title": issue_title,
                "body": new_hash
            }
        )

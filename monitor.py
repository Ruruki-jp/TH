import os
import hashlib
import requests

URL = "https://steamdb.info/app/3678970/history/"

# 環境変数の取得
WEBHOOK = os.environ["DISCORD_WEBHOOK"]
TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]

# SteamDB取得（Cloudflare等のボット対策を極力回避するためのヘッダー）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# SteamDBのHTMLを取得
try:
    res = requests.get(URL, headers=headers)
    res.raise_for_status()  # 200以外（403エラー等）ならここで処理を止める
    html = res.text
except Exception as e:
    print(f"SteamDBの取得に失敗（スクレイピングブロックされた可能性あり）: {e}")
    exit(1)

new_hash = hashlib.sha256(html.encode()).hexdigest()

# GitHub APIの設定
issue_title = "STEAMDB_HASH"
api_headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

# 既存Issue検索（1ページ目の上限で見失わないよう、タイトル指定で検索）
search_url = f"https://api.github.com/search/issues?q=repo:{REPO}+type:issue+state:open+in:title+{issue_title}"
try:
    search_res = requests.get(search_url, headers=api_headers)
    search_res.raise_for_status()
    items = search_res.json().get("items", [])
except Exception as e:
    print(f"GitHub API（Issue検索）に失敗しました: {e}")
    exit(1)

issue = None
for i in items:
    if i["title"] == issue_title:
        issue = i
        break

old_hash = ""
if issue:
    old_hash = issue["body"].strip()

# 比較と通知・更新
if old_hash != new_hash:
    # Discord通知
    requests.post(
        WEBHOOK,
        json={
            "content": f"🔔 Task Bar Hero SteamDB 更新！\n{URL}"
        }
    )

    if issue:
        # Issue更新
        requests.patch(
            issue["url"],
            headers=api_headers,
            json={"body": new_hash}
        )
        print("状態（Issue）を更新しました。")
    else:
        # 初回Issue作成
        requests.post(
            f"https://api.github.com/repos/{REPO}/issues",
            headers=api_headers,
            json={
                "title": issue_title,
                "body": new_hash
            }
        )
        print("初回用の状態保存Issueを作成しました。")
else:
    print("更新はありませんでした。")

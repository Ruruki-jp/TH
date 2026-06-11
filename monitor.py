import os
import hashlib
import cloudscraper

URL = "https://steamdb.info/app/3678970/history/"

# 環境変数の取得
WEBHOOK = os.environ["DISCORD_WEBHOOK"]
TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]

# cloudscraperの起動（Cloudflare対策）
scraper = cloudscraper.create_scraper()

try:
    # 通常のrequestsではなくscraperを使うことで403エラーを回避します
    res = scraper.get(URL)
    res.raise_for_status()
    html = res.text
except Exception as e:
    print(f"SteamDBの取得に失敗しました: {e}")
    exit(1)

# HTMLからハッシュ値を生成
new_hash = hashlib.sha256(html.encode()).hexdigest()

# GitHub APIの設定
issue_title = "STEAMDB_HASH"
api_headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

# 既存Issue検索
search_url = f"https://api.github.com/search/issues?q=repo:{REPO}+type:issue+state:open+in:title+{issue_title}"
search_res = scraper.get(search_url, headers=api_headers)
search_res.raise_for_status()
items = search_res.json().get("items", [])

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
    scraper.post(
        WEBHOOK,
        json={
            "content": f"🔔 Task Bar Hero SteamDB 更新！\n{URL}"
        }
    )

    if issue:
        # Issue更新
        scraper.patch(
            issue["url"],
            headers=api_headers,
            json={"body": new_hash}
        )
        print("Issueのハッシュ値を更新しました。")
    else:
        # 初回Issue作成
        scraper.post(
            f"https://api.github.com/repos/{REPO}/issues",
            headers=api_headers,
            json={
                "title": issue_title,
                "body": new_hash
            }
        )
        print("初回用のIssueを作成しました。")
else:
    print("変更はありませんでした。")

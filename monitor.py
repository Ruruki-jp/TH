import os
import requests

# Task Bar Hero の AppID
APP_ID = "3678970"
# 誰でもアクセスできるSteam公式のアプリ更新情報API（100%ブロックされません）
URL = f"https://api.steampowered.com/ISteamApps/UpToDateCheck/v1/?appid={APP_ID}&version=0"
STEAMDB_PAGE = f"https://steamdb.info/app/{APP_ID}/history/"

# 環境変数の取得
WEBHOOK = os.environ["DISCORD_WEBHOOK"]
TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPOSITORY"]

# Steam公式APIからデータを取得
try:
    res = requests.get(URL)
    res.raise_for_status()
    data = res.json()
    
    # APIのレスポンスから「現在の最新ChangeID（型番のようなもの）」を抽出
    # ※このAPIは、現在の最新ChangeIDをレスポンスの「required_version」という項目に返してくれます
    success = data.get("response", {}).get("success", False)
    if not success:
        print("Steam APIからのデータ取得に失敗しました（success=false）")
        exit(1)
        
    new_change_id = str(data.get("response", {}).get("required_version", ""))
    
    if not new_change_id:
        print("ChangeIDの取得に失敗しました。")
        exit(1)
        
except Exception as e:
    print(f"Steam APIの取得に失敗しました: {e}")
    exit(1)

# GitHub APIの設定
issue_title = "STEAMDB_HASH"  # 管理用のIssueタイトル（名前はそのままでOK）
api_headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

# 既存Issue検索
search_url = f"https://api.github.com/search/issues?q=repo:{REPO}+type:issue+state:open+in:title+{issue_title}"
search_res = requests.get(search_url, headers=api_headers)
search_res.raise_for_status()
items = search_res.json().get("items", [])

issue = None
for i in items:
    if i["title"] == issue_title:
        issue = i
        break

old_change_id = ""
if issue:
    old_change_id = issue["body"].strip()

# 前回とChangeIDが違う＝アップデートがあった場合
if old_change_id != new_change_id:
    # Discord通知
    requests.post(
        WEBHOOK,
        json={
            "content": f"🔔 Task Bar Hero にアップデート（更新）が来ました！\n{STEAMDB_PAGE}"
        }
    )

    if issue:
        # Issueの更新
        requests.patch(
            issue["url"],
            headers=api_headers,
            json={"body": new_change_id}
        )
        print(f"現在の状態（ChangeID: {new_change_id}）を更新しました。")
    else:
        # 初回Issue作成
        requests.post(
            f"https://api.github.com/repos/{REPO}/issues",
            headers=api_headers,
            json={
                "title": issue_title,
                "body": new_change_id
            }
        )
        print(f"初回用の状態保存Issueを作成しました。（ChangeID: {new_change_id}）")
else:
    print(f"現在のChangeID ({new_change_id}) からアップデートはありませんでした。")

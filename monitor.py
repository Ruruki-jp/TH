import os
import hashlib
import requests

URL = "https://steamdb.info/app/3678970/history/"

WEBHOOK = os.environ["DISCORD_WEBHOOK"]

STATE = "last_hash.txt"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(URL, headers=headers).text

new_hash = hashlib.sha256(html.encode()).hexdigest()

old_hash = ""

if os.path.exists(STATE):
    with open(STATE, "r") as f:
        old_hash = f.read()

if new_hash != old_hash:

    requests.post(
        WEBHOOK,
        json={
            "content":
            f"🔔 **Task Bar Hero SteamDBが更新されました！**\n{URL}"
        }
    )

    with open(STATE, "w") as f:
        f.write(new_hash)

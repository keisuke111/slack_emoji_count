import requests
import json
import time

token = ""
params = { "token": token }

# -----------------
# チャンネル一覧を取得
# -----------------

r = requests.get("https://slack.com/api/channels.list", params=params)
json = r.json()

# PublicChannelのIDを格納
channels = []

for channel in json["channels"]:
    channels.append(channel["id"])

print("パブリックチャンネル数: ", len(channels))

# --------------------
# カスタム絵文字一覧を取得
# --------------------

r = requests.get("https://slack.com/api/emoji.list", params=params)
json = r.json()

# カスタム絵文字を格納
emojis = {}

for emoji in json["emoji"]:
    emojis.update({ f"{emoji}" : 0 })

print("カスタム絵文字数: ", len(emojis))

# --------------------------------------------------
# チャンネルのメッセージ履歴を取得、カスタム絵文字の使用回数を計測
# --------------------------------------------------

for channel in channels:
    params = {
        "token": token,
        "count": 1000,
        "channel": channel
    }

    r = requests.get("https://slack.com/api/channels.history", params=params)
    json = r.json()

    # メッセージがない時
    if "messages" in json == False:
        continue

    # チャンネルのメッセージ分（MAX1000）
    for message in json["messages"]:
        if "reactions" in message:
            # ついたリアクションの種類分
            for reaction in message["reactions"]:
                # カスタム絵文字から探して数を更新
                for emoji, count in emojis.items():
                    if emoji == reaction["name"]:
                        emojis[emoji] = count + reaction["count"]

    time.sleep(1)

# ソート
emojis_sorted = sorted(emojis.items(), key=lambda x:x[1], reverse=True)[:30]

# ファイルに出力
f = open('result.txt', 'w')
for data in emojis_sorted:
    f.write(str(data) + "\n")
f.close()

import requests
import json
import time
import sys


# -----------------
# チャンネル一覧を取得
# -----------------
def get_channel_list(params):
    r = requests.get("https://slack.com/api/channels.list", params=params)
    json = r.json()

    # PublicChannelのIDを格納
    channels = []

    for channel in json["channels"]:
        channels.append(channel["id"])

    print("パブリックチャンネル数: ", len(channels))
    return channels


# --------------------------------------------
# チャンネルのメッセージ履歴を取得、絵文字の使用回数を計測
# --------------------------------------------
def count_emoji(channels, param):
    # 絵文字を格納
    emojis = {}

    for channel in channels:
        params.update(count=1000, channel=channel)

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
                    # 集計リストに追加
                    if reaction["name"] in emojis:
                        emojis[reaction["name"]] += reaction["count"]
                    else:
                        emojis[reaction["name"]] = reaction["count"]
        
        # 制限対策
        time.sleep(1)

    print("絵文字数: ", len(emojis))
    return emojis


# --------------------
# カスタム絵文字一覧を取得
# --------------------
def get_custom_emoji(params):
    r = requests.get("https://slack.com/api/emoji.list", params=params)
    json = r.json()

    # カスタム絵文字を格納
    emojis = {}

    for emoji in json["emoji"]:
        emojis.update({ f"{emoji}" : 0 })

    print("カスタム絵文字数: ", len(emojis))
    return emojis


# --------------------------------------------------
# チャンネルのメッセージ履歴を取得、カスタム絵文字の使用回数を計測
# --------------------------------------------------
def count_custom_emoji(channels, emojis, params):
    for channel in channels:
        params.update(count=1000, channel=channel)

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

        # 制限対策
        time.sleep(1)
    
    return emojis


# ------------------------
# 使用回数の多い順（30個）にソート
# ------------------------
def sort_30(emojis):
    emojis_sorted = sorted(emojis.items(), key=lambda x:x[1], reverse=True)[:30]

    return emojis_sorted


if __name__ == '__main__':
    token = ""
    params = { "token": token }

    # 引数でモードを判断
    if len(sys.argv) == 2:
        channel = get_channel_list(params)

        if sys.argv[1] == 'all':        # 全絵文字のランキング
            emojis = count_emoji(channel, params)
        elif sys.argv[1] == 'custom':   # カスタム絵文字のランキング
            custom_emojis = get_custom_emoji(params)
            emojis = count_custom_emoji(channel, custom_emojis, params)
        else:
            print('$ python main.py <all or cumtom>')
            quit()
    else:
        print('$ python main.py <all or cumtom>')
        quit()

    emojis_sorted = sort_30(emojis)
    # ファイルに出力
    f = open('result.txt', 'w')
    for data in emojis_sorted:
        f.write(str(data) + "\n")
    f.close()

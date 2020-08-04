import config
import json # 標準のjsonモジュールとconfig.pyの読み込み
from requests_oauthlib import OAuth1Session #OAuthのライブラリの読み込み

CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CK, CS, AT, ATS) #認証処理

screen_name = 'KasperProducer'
user_id = '1060563350478708736'
tweet_id = '1281061152848351241'

seen = {}
reply_with_img = []

#timelineの取得
def get_timeline(user_id):
    tl = None
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json" #タイムライン取得エンドポイント
    params ={
        'user_id' : user_id,
        'count' : 200
        } #取得数
    res = twitter.get(url, params = params)
    if res.status_code == 200: #正常通信出来た場合
        tl = json.loads(res.text) #レスポンスからタイムラインリストを取得
    else: #正常通信出来なかった場合
        raise Exception("Failed: %d" % res.status_code)
    return tl

def make_only_selfreply(tl, tweet_id):
    selfreplies = {}
    reply_tree = {}
    for tweet in tl:
        if tweet['id_str'] == tweet_id:
            selfreplies[tweet['id_str']] = tweet

        if (tweet['in_reply_to_status_id_str'] is not None) and (tweet['in_reply_to_user_id_str'] == user_id):
            if tweet['in_reply_to_status_id_str'] in reply_tree:
                reply_tree[tweet['in_reply_to_status_id_str']].append(tweet['id_str'])
            else:
                reply_tree[tweet['in_reply_to_status_id_str']] = [tweet['id_str']]

            selfreplies[tweet['id_str']] = tweet
    return {'reply_tree' : reply_tree, 'selfreplies': selfreplies}

#リプライの再帰取得
def reply_with_img_dfs(selfreplies, reply_tree, tweet_id):
    global seen, reply_with_img
    media_url = tweet_to_media_url(selfreplies[tweet_id])
    if media_url is not None:
        reply_with_img.append([tweet_id, media_url])
        # print('*', tweet_id, media_url)
    if tweet_id not in reply_tree or seen[tweet_id]:
        return None
    for reply_id in reply_tree[tweet_id]:
        reply_with_img_dfs(selfreplies, reply_tree, reply_id)
        seen[tweet_id] = 1

def tweet_to_media_url(tweet):
    if 'media' in tweet['entities']:
        for media in tweet['entities']['media']:
            return media['media_url']
    else:
        return None

def main():
    global seen, reply_with_img
    tl = get_timeline(user_id)
    res = make_only_selfreply(tl, tweet_id)
    reply_tree = res['reply_tree']
    selfreplies = res['selfreplies']
    """
    for tree in reply_tree:
        print(reply_tree[tree])
    for reply in selfreplies:
        print(selfreplies[reply]['text'])
    """
    seen = {key : 0 for key in selfreplies}
    reply_with_img_dfs(selfreplies, reply_tree, tweet_id)
    for d in reply_with_img:
        print(d)

if __name__ == "__main__":
    main()
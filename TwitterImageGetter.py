# coding: utf-8

import tweepy
import pandas as pd
import datetime
import time

import os, sys, traceback
import config
import urllib.error
import urllib.request
import json


class TwitterImageGetter():
    def __init__(self, directory_name):
        consumer_key = config.CONSUMER_KEY
        consumer_secret = config.CONSUMER_SECRET
        auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
        self.api = tweepy.API(auth)
        self.directory_name = directory_name
        path = r'./{}'.format(directory_name)
        if not os.path.isdir(path):
            os.makedirs(path)
        self.tweet_data = []
        self.image_url = []
        
    def get_tweet(self, text):
        print("start")
        search_text = '{} AND filter:media -filter:retweets min_retweets:20'.format(text)
        print(search_text)
        for result_tweet in tweepy.Cursor(self.api.search, q=search_text, count=100, tweet_mode='extended', wait_on_rate_limit = True).items():
            # print('media' in result_tweet.entities)
            tweet = {}
            tweet['tweet_id'] = result_tweet.id_str
            tweet['user_id'] = result_tweet.user.id_str
            tweet['screen_name'] = result_tweet.user.screen_name
            tweet['text'] = result_tweet.full_text
            tweet['created_at'] = result_tweet.created_at
            tweet['followers_count'] = result_tweet.user.followers_count
            tweet['friends_count'] = result_tweet.user.friends_count
            tweet['retweet_count'] = result_tweet.retweet_count
            tweet['id_downloaded'] = False
            # print('media' in result_tweet.extended_entities)
            if 'media' in result_tweet.extended_entities:
                tweet['media'] = result_tweet.extended_entities['media']
                self.tweet_data.append(tweet)
        print("end")
    
    def download_all_image(self):
        for (di, d) in enumerate(self.tweet_data):
            print(d['created_at'])
            for (mi, media) in enumerate(d['media']):
                url = '%s:orig' % media['media_url_https']
                dst_path = './{0}/{0}_{1:03d}_{2}.jpg'.format(self.directory_name, di+1, mi+1)
                print(dst_path)
                # dst_dir = 'data/src'
                # dst_path = os.path.join(dst_dir, os.path.basename(url))
                self.download_image(url, dst_path)
    
    def download_image(self, url, dst_path):
        try:
            data = urllib.request.urlopen(url).read()
            with open(dst_path, mode="wb") as f:
                f.write(data)
        except urllib.error.URLError as e:
            print(e)


# 検索データ収納先
# Twitterからタグで検索
# 画像URLから画像を取得
def main():
    full_name = '豊川風花'
    first_name = '風花'
    texts = ['#{0}生誕祭2019 OR #{0}生誕祭 OR #{0}誕生祭 OR #{0}誕生祭2019', '{1} AND 誕生' ,'{1} AND "おめでと"']
    texts = [x.format(full_name, first_name) for x in texts]
    texts =['#周防桃子']
    directory_name = 'test2'
    getter = TwitterImageGetter(directory_name)
    for text in texts:
        getter.get_tweet(text)

    getter.download_all_image()


if __name__ == "__main__":
    main()
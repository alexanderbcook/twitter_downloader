#!/usr/bin/env python

#USAGE: python downloader.py realDonaldTrump

import tweepy
import csv
import config
import logging
import sys

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def get_all_tweets(user_name):

    # Initialize list
    tweets = []

    # Initial API request
    tweet_block = api.user_timeline(screen_name = user_name,count=200)
    tweets.extend(tweet_block)
    last = tweets[-1].id - 1

    # Form a queue of all remaining tweets.
    while len(tweet_block) > 0:

        tweet_block = api.user_timeline(screen_name = user_name,count=200,max_id=last)
        tweets.extend(tweet_block)
        last = tweets[-1].id - 1

        logging.debug('Collected %s tweets.' % len(tweet_block))

    # Flatten tweets into array
    flattened_tweet = [tweet.text.encode("utf-8") for tweet in tweets]
    with open('input.txt', 'wb') as f:
        f.write(str(flattened_tweet))
    '''
    logging.debug('Writing tweets to %s.csv' % user_name)
    with open('data/%s.csv' % user_name, 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(flattened_tweet)
    '''
    pass

if __name__ == '__main__':
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_secret)
    api = tweepy.API(auth)
    logging.debug('Twitter API successfully authorized.')
    get_all_tweets(str(sys.argv[1]))
#!/usr/bin/env python

#USAGE: python downloader.py -u realDonaldTrump -t db

import tweepy
import csv
import argparse
import psycopg2
import logging
import config
from util import encode

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u",
                        "--user",
                        dest="user_name",
                        help="Enter the username of the twitter account from which you would like to collect tweets.")
    parser.add_argument("-t",
                        "--output",
                        dest="output",
                        help="Enter 'csv' to produce a csv file, or 'db' to upload to a database.",
                        default='csv')
    return parser

parser = get_parser()
args = parser.parse_args()

def encode(string):
    if string:
        string = string.encode('utf-8')
    return string

def get_all_tweets(user_name):

    # Initialize list
    tweets = []

    # Initial API request
    tweet_block = api.user_timeline(screen_name=args.user_name, count=200)
    tweets.extend(tweet_block)
    last = tweets[-1].id - 1

    # Form a queue of all remaining tweets.
    while len(tweet_block) > 0:

        tweet_block = api.user_timeline(screen_name=args.user_name, count=200, max_id=last)
        tweets.extend(tweet_block)
        last = tweets[-1].id - 1

        logging.debug('Collected %s tweets.' % len(tweet_block))

    # Flatten tweets into data carrying list
    if args.output == 'csv':
        # Write to a CSV file. The name of the file will just be the name of the user.
        data = [tweet for tweet in tweets]

        logging.debug('Writing tweets to data/%s.csv' % args.user_name)

        csvFile = open('%s.csv' % (args.user_name), 'a')
        csvWriter = csv.writer(csvFile)

        for datum in data:
            csvWriter.writerow([datum.created_at, encode(datum.text), datum.id, encode(datum.user.location)])

    elif args.output == 'db':
        # Write to database specified in config.py file.
        # Note that this will not work if the twitter schema has not been created yet.
        conn = psycopg2.connect(config.conn_string)
        cursor = conn.cursor()
        logging.debug('Connected database and writing tweets to %s' % config.conn_string)

        data = [tweet for tweet in tweets]

        for datum in data:
            cursor.execute('CREATE TABLE IF NOT EXISTS twitter.%s (date date, text varchar, id bigint, location varchar);'
                           % args.user_name)
            cursor.execute('INSERT INTO twitter.%s (date, text, id, location) VALUES ("%s", "%s", "%s", "%s");'
                           % (args.user_name, datum.created_at, encode(datum.text), datum.id, encode(datum.user.location)))


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
    auth.set_access_token(config.access_token, config.access_secret)
    api = tweepy.API(auth)
    logging.debug('Twitter API successfully authorized.')
    get_all_tweets(args.user_name)
# -*- coding: utf-8 -*-
import os
import os.path
import argparse

from twitter.stream import *
from twitter.api import *
from twitter.oauth import OAuth, read_token_file
from twitter.oauth_dance import oauth_dance
from twitter.util import printNicely
from multiprocessing import Process
from db import *

db=AskDB()
g={}

def authen():
    """
    Authenticate with Twitter OAuth
    """
    CONSUMER_KEY = '9v0gwkxQeWwnCXfMwuIevRAZA'
    CONSUMER_SECRET = 'wHP4NZ1tHxVFFyTAM8KGKHpxmPg3ErY4ibYxLftxjrPBKmJLvt'
    # When using rainbow stream you must authorize.
    twitter_credential = os.environ.get(
        'HOME',
        os.environ.get(
            'USERPROFILE',
            '')) + os.sep + '.askbot_oauth'
    if not os.path.exists(twitter_credential):
        oauth_dance("Dwango Ask",
                    CONSUMER_KEY,
                    CONSUMER_SECRET,
                    twitter_credential)
    oauth_token, oauth_token_secret = read_token_file(twitter_credential)
    return OAuth(
        oauth_token,
        oauth_token_secret,
        CONSUMER_KEY,
        CONSUMER_SECRET)


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__ or "")
    parser.add_argument(
        '-to',
        '--timeout',
        help='Timeout for the stream (seconds).')
    parser.add_argument(
        '-ht',
        '--heartbeat-timeout',
        help='Set heartbeat timeout.',
        default=90)
    parser.add_argument(
        '-nb',
        '--no-block',
        action='store_true',
        help='Set stream to non-blocking.')
    parser.add_argument(
        '-tt',
        '--track-keywords',
        help='Search the stream for specific text.')
    return parser.parse_args()

def stream():

    args = parse_arguments()
    domain = 'userstream.twitter.com'
    # These arguments are optional:
    stream_args = dict(
        timeout=args.timeout,
        block=not args.no_block,
        heartbeat_timeout=args.heartbeat_timeout)

    # Track keyword
    query_args = dict()
    if args.track_keywords:
        query_args['track'] = args.track_keywords

    # Get stream
    stream = TwitterStream(
        auth=authen(),
        domain=domain,
        **stream_args)

    tweet_iter = stream.user(**query_args)
    for tweet in tweet_iter:
        if tweet is None:
            printNicely("-- None --")
        elif tweet is Timeout:
            printNicely("-- Timeout --")
        elif tweet is HeartbeatTimeout:
            printNicely("-- Heartbeat Timeout --")
        elif tweet is Hangup:
            printNicely("-- Hangup --")
        elif tweet.get('text'):
            try:
                reply(tweet)
            except Exception,e:
                print e
        elif tweet.get('direct_message'):
            try:
                process(tweet['direct_message'])
            except Exception,e:
                print e

def reply(tweet):
    t = Twitter(auth=authen())
    screen_name = tweet['user']['screen_name']
    text = tweet['text'].strip()
    if text.split()[0] == '@dwango_ask':
        text = ' '.join(text.split()[1:])
        # Receiver
        if text == 'receiver':
            status = '@'+ screen_name
            for r in g['receiver']:
                status += ' '+r
            t.statuses.update(status=status)
        elif text.split()[0] == '#rep':
            id = text.split()[1]
            answer = ' '.join(text.split()[2:])
            db.store_answer(id, answer)
            question = db.query_question(id)
            question = ' '.join(question.split()[1:])
            status = '@' + screen_name + ' answered \"' + question +'\"'
            t.statuses.update(status=status)
            status = '\"' + answer + '\"'
            t.statuses.update(status=status)

def process(m):
    t = Twitter(auth=authen())
    sender = m['sender_screen_name']
    recipient = m['recipient_screen_name']
    g['receiver'].append(sender)
    text = m['text']
    ary = text.split()
    if not ary[0].startswith('@'):
        printNicely('Ignore message')
    else:
        id = db.store_question(text) 
        status = text + '(answer with #rep ' + str(id) + ')'
        t.statuses.update(status=status)


def listen():
    t = Twitter(auth=authen())
    rel = t.direct_messages(count=20,cur_page=1,include_entities=False,skip_status=True)
    for m in reversed(rel):
        try:
            process(m)
        except:
            pass

if __name__ == '__main__':
    g['receiver'] = []
    p = Process(target=stream)
    p.start() 
    #listen()

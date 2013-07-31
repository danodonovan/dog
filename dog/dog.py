#!/usr/bin/env python
# encoding: utf-8
"""
dog.py

Created by Daniel O'Donovan on 2011-11-10.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import time
from datetime import timedelta
import random
import logging
from logging.handlers import RotatingFileHandler
import json

import twitter

# load the twitter messages
good_dog_messages = open('good_dog.txt').readlines()
bad_dog_messages = open('bad_dog.txt').readlines()

# load the last message id
with open('config.json', 'r') as fd:
    config = json.load(fd)

def setup_logging(  level=logging.DEBUG,
                    filename='/var/log/dog.log',
                    format="%(asctime)s - %(levelname)s :: %(message)s",
                    rotate_logs=False):
    """ Setup Logging
            For logging from multiple files
    """
    log = logging.getLogger('dogd')
    log.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter(format)

    # creates a new log file for each running instance (and renames old one)
    if rotate_logs:
        txt_handler = RotatingFileHandler(filename, backupCount=5)
        txt_handler.doRollover()
    else:
        txt_handler = logging.FileHandler(filename)
    txt_handler.setFormatter(log_formatter)

    log.addHandler(txt_handler)
    log.info("logger initialised")

    return txt_handler

def get_random_bark( bark_type=None ):
    """ Return a random bark
            Input: (optional) 'good' or 'bad'
    """
    doglog = logging.getLogger('dogd')
    doglog.debug('get_random_bark %s' % bark_type)

    if bark_type and bark_type.lower() in ('good', 'bad'):
        if bark_type.lower() is 'good':
            messages = good_dog_messages
        else:
            messages = bad_dog_messages
    else:
        messages = good_dog_messages + bad_dog_messages

    return random.choice(messages).strip()

def random_bark_loop(api, bark_interval=timedelta(hours=0.7)):
    """ Random Bark loop
            This randomly posts a message in to twitter stream
            Input: Twitter API object
    """
    doglog = logging.getLogger('dogd')
    doglog.debug('random_bark_loop')

    # execute once a minute
    n_secs = bark_interval.seconds if type(bark_interval) is timedelta else 2520
    doglog.debug('bark interval %d' % n_secs)

    # the main loop
    while True:
        # update status
        tweet = get_random_bark()
        doglog.debug('posting status - "%s"' % tweet)

        status = api.PostUpdate( tweet )

        if status:
            doglog.debug('status sent - "%s"' % status.text)

        # wait
        time.sleep( n_secs )

def respond_bark(api, reply_interval=timedelta(minutes=0.5)):
    """ Respond Bark
            This function responds to a received tweet
    """
    doglog = logging.getLogger('dogd')
    doglog.debug('respond_bark')

    n_secs = reply_interval.seconds if type(reply_interval) is timedelta else 30
    doglog.debug('reply interval %d' % n_secs)

    last_id = config['last_id']

    while True:
        # get new mentions
        mentions = api.GetMentions( since_id=last_id )
        last_id = mentions[-1].id if mentions else last_id

        # process mentions and send replies
        for m in mentions:

            tweet = get_random_bark(bark_type='good')
            update = '@%s %s' % (m.user.screen_name, tweet)

            doglog.debug( 'posting reply to %s - "%s"' % ( m.user.name, update ) )
            status = api.PostUpdates( update )

        config['last_id'] = last_id
        with open(CONF_FILE) as fd:
            json.dump(config, fd)

        # wait a bit before zipping round again
        time.sleep(reply_interval)

if __name__ == '__main__':
    pass



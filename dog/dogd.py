#!/usr/bin/env python
# encoding: utf-8
"""
dogd.py

Created by Daniel O'Donovan in 2013 somtime.
Copyright (c) 2013. All rights reserved.
"""
import json
import logging

from daemon import runner
import twitter

from dog_2 import DogBot, setup_logging

# load the last message id
with open('good.config.json', 'r') as fd:
    config = json.load(fd)

# set up the logging
doglog_handler = setup_logging(filename=config['LOG_FILE'])

doglog = logging.getLogger('dogd')
doglog.setLevel(logging.DEBUG)

# set up the twitter api
api = twitter.Api(
    consumer_key=config['CONSUMER_KEY'],
    consumer_secret=config['CONSUMER_SECRET'],
    access_token_key=config['ACCESS_TOKEN_KEY'],
    access_token_secret=config['ACCESS_TOKEN_SECRET']
)

db = DogBot(api, config['last_id'], logger=doglog)

daemon_runner = runner.DaemonRunner(db)
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[doglog]
daemon_runner.do_action()



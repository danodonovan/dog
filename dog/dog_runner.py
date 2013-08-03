#!/usr/bin/env python
# encoding: utf-8
"""
dog_runner.py

Created by Daniel O'Donovan in 2013 somtime.
Copyright (c) 2013. All rights reserved.
"""
import json
import logging

import twitter

from dog import DogBot

# load the last message id
with open('config.json', 'r') as fd:
    config = json.load(fd)

# set up the logging
doglog = logging.getLogger('dogd')
doglog.setLevel(logging.DEBUG)

if 'LOG_FILE' in config:
    formatter = logging.Formatter("%(asctime)s - %(levelname)s :: %(message)s",)
    handler = logging.FileHandler(config['LOG_FILE'])
    handler.setFormatter(formatter)
    doglog.addHandler(handler)
else:
    logging.basicConfig()

# authenticate with the twitter api
api = twitter.Api(
    consumer_key=config['CONSUMER_KEY'],
    consumer_secret=config['CONSUMER_SECRET'],
    access_token_key=config['ACCESS_TOKEN_KEY'],
    access_token_secret=config['ACCESS_TOKEN_SECRET']
)

db = DogBot(api, config['last_id'], logger=doglog)

db.run_once()

# update the config before we quit
with open('config.json', 'w') as fd:
    config['last_id'] = db.last_id
    json.dump(config, fd)
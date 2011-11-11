#!/usr/bin/env python
# encoding: utf-8
"""
dogd.py

Created by Daniel O'Donovan on 2011-10-20.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
import sys
import time
import json
import logging
from multiprocessing import Process

import daemon
from daemon.pidfile import TimeoutPIDLockFile
import twitter

from dog import random_bark_loop, respond_bark, setup_logging

# load the last message id
with open('config.json', 'r') as fd:
    config = json.load(fd)

# set up the logging
doglog_handler = setup_logging(filename=config['LOG_FILE'])
doglog = logging.getLogger('dogd')

# set up the twitter api
api = twitter.Api(  consumer_key=config['CONSUMER_KEY'],
                    consumer_secret=config['CONSUMER_SECRET'], 
                    access_token_key=config['ACCESS_TOKEN_KEY'], 
                    access_token_secret=config['ACCESS_TOKEN_SECRET'])

if api:
    doglog.debug("twitter api initialised")
else:
    doglog.error("twitter api initialise failed")
    sys.exit()

pid = TimeoutPIDLockFile(
    "/tmp/odonovan-daemon-dogd.pid", 10)

daemonContext = daemon.DaemonContext(
    pidfile=pid,
    files_preserve=[doglog_handler.stream])

# start daemon contexts
with daemonContext:
    # one process to send random barks, one to respond to incoming tweets
    doglog.debug("starting random bark process")
    rand_b = Process(target=random_bark_loop, args=(api,))

    doglog.debug("starting respond bark process")
    resp_b = Process(target=respond_bark, args=(api,))

    rand_b.start()
    resp_b.start()

doglog.debug("finishing up daemon")
# clean up
rand_b.join()
resp_b.join()




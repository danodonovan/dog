#!/usr/bin/env python
# encoding: utf-8
"""
dog_2.py

Created by Daniel O'Donovan in 2013 sometime
Copyright (c) 2013. All rights reserved.
"""
import time
import random
from datetime import timedelta
import logging

import twitter


class TwitterBot(object):
    
    def __init__(self, api, logger=None):
        self.api = api
        self.logger = logger
        
    def follow_followers(self):
        """ follow_followers
        Follow everyone who follows you
        """
        friends_names = [u.screen_name for u in self.api.GetFriends()]
        for user in self.api.GetFollowers():
            if user.screen_name not in friends_names:
                self.logger.debug('new follow %s' % user.screen_name)
                status = self.api.CreateFriendship(user.user_id)
                self.logger.debug('status: %s' % status)
                
    def respond(self, user, message):
        """ respond
        Respond to a received user
        """
        update = '@%s %s' % (user, message)
        self.logger.debug('respond "%s"' % update)
        status = self.api.PostUpdates(update)
        self.logger.debug('status: %s' % status)

    def tweet(self, message):
        """ tweet
        send a tweet
        """
        self.logger.debug('tweet "%s"' % message)
        status = self.api.PostUpdates(message)
        self.logger.debug('status: %s' % status)


class DogBot(TwitterBot):
    
    def __init__(self, api, last_id, logger=None, good_dog_file='good_dog.txt', bad_dog_file='bad_dog.txt'):
        
        super(DogBot, self).__init__(api, logger)

        self.last_id = last_id
        self.good_dog_messages = open(good_dog_file).readlines()
        self.bad_dog_messages = open(bad_dog_file).readlines()

        # daemon bits
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/var/run/testdaemon.pid'
        self.pidfile_timeout = 5

    def random_bark(self, bark_type=None):
        """ random_bark
        bark_type: 'good' or 'bad'
        returns a random bark
        """
        if bark_type is None:
            bark_type = random.choice(['good', 'bad'])

        bark_type = bark_type.lower()
        if bark_type in ('good', 'bad'):
            if bark_type == 'good':
                return random.choice(self.good_dog_messages).strip()
            else:
                return random.choice(self.bad_dog_messages).strip()
    
    def run(self, wait_interval=timedelta(hours=1.3)):
        # if python had decent threading I would create two threads, 
        # one to respond to mentions, one to tweet randomly
        while True:
        
            # get new mentions
            mentions = self.api.GetMentions(since_id=self.last_id)
            self.m = mentions

            # process mentions and send replies
            for m in mentions:

                message = self.random_bark(bark_type='good')
                self.respond(m.user.screen_name, message)
            
            # update so don't resend tweets
            self.last_id = mentions[-1].id if mentions else last_id

            # update status
            self.tweet(self.random_bark())

            # wait a bit before zipping round again
            time.sleep(wait_interval.seconds)

def setup_logging(level=logging.DEBUG,
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
#!/usr/bin/env python
# encoding: utf-8
"""
dog.py

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
        try:
            status = self.api.PostUpdates(update)
            self.logger.debug('posted')
        except twitter.TwitterError as e:
            self.logger.error('respond exception: %s' % e)


    def tweet(self, message):
        """ tweet
        send a tweet
        """
        self.logger.debug('tweet "%s"' % message)
        try:
            status = self.api.PostUpdates(message)
            self.logger.debug('posted')
        except twitter.TwitterError as e:
            self.logger.error('tweet exception: %s' % e)


class DogBot(TwitterBot):
    
    def __init__(self, api, last_id, logger=None, 
            good_dog_file='good_dog.txt', bad_dog_file='bad_dog.txt'):
        
        super(DogBot, self).__init__(api, logger)

        self.last_id = last_id
        self.good_dog_messages = open(good_dog_file).readlines()
        self.bad_dog_messages = open(bad_dog_file).readlines()

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
    
    def run_once(self):
        """ run_once
        run once through the dog responses, bark, respond, follow etc.
        """

        # process mentions and send replies
        for mention in self.api.GetMentions(since_id=self.last_id):

            message = self.random_bark(bark_type='good')
            self.respond(mention.user.screen_name, message)
    
            # update so don't resend tweets
            self.last_id = mention.id if mention.id > self.last_id else self.last_id

        # follow back new followers
        self.follow_followers()

        # update status
        self.tweet(self.random_bark())
    
    
    def run(self, wait_interval=timedelta(hours=1.3)):
        """ run
        do all the things the dog should do, in a continuous while loop
        """
        # if python had decent threading I would create several threads, 
        # one to respond to mentions, one to tweet randomly etc.
        while True:
        
            self.run_once()
            
            # wait a bit before zipping round again
            time.sleep(wait_interval.seconds)
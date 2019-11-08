# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 14:24:48 2019

@author: mctwn

This strategy is the following:
    1. Search for those posts where ppl comment and follow those who liked 
    their comments
    2. Like all comments
    3. Follow back those who followed you

"""
   
#print(results[0])
#json_str = json.dumps(replies[0]._json)
#print(json_str)

#############################################################

import tweepy
import json
from time import sleep
from re import search
from itertools import cycle
from random import shuffle, randint
from datetime import datetime, timedelta
from config import *
from sys import exit




class TwitterBot(object):
    """docstring for TwitterBot"""
    def __init__(self):
        # authorization from values inputted earlier, do not change.
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_secret)
        self.api = tweepy.API(auth, proxy = proxy)
        self.followers = self.api.followers_ids(screen_name)
        self.following = self.api.friends_ids(screen_name)
        self.max_unfollow = max_unfollow
        self.max_follow = max_follow

    def retweet_like_follow_by_keywords(self): #origine
        for i in keywords:
            print("selected search text:", i)
            for twi in tweepy.Cursor(self.api.search, q=i).items(results_search):
                try:
                    twi.retweet()
                    twi.favorite()
                except tweepy.TweepError as e:
                    print(e)
                except:
                    print("Unknow Exception come!!")
                if not twi.user.following and twi.user.screen_name!=screen_name:
                    twi.user.follow()
                    print('Followed user. Sleeping 15 seconds.')
                    sleep(15)
        print("Completed")
    
    def delete_tweet(self):                     #origine
        cutoff_date = datetime.utcnow() - timedelta(days=tweet_delete_days)
        # get all timeline tweets
        print("Retrieving timeline tweets")
        for tweet in tweepy.Cursor(self.api.user_timeline).items(150):
            # import pdb;pdb.set_trace()
            if tweet.id and tweet.created_at > cutoff_date:
                #print(tweet.created_at > cutoff_date,tweet.created_at, cutoff_date)
                try:
                    if tweet.user.screen_name!=tweet.retweeted_status.user.screen_name:
                        print("Deleting %d: [%s] %s" % (tweet.id, tweet.created_at, tweet.text))
                        #self.api.destroy_status(tweet.id)
                except:
                    print("Its not a ReTweet!!")
        print("Job Complted, tweets deleted!!")
        
    def unfollow_back_who_not_follow_me(self):   #origine
        # function to unfollow users that don't follow you back.
        print('Starting to unfollow users...')
        # makes a new list of users who don't follow you back.
        non_mutuals = set(self.following) - set(self.followers)
        total_followed = 0
        for f in non_mutuals:
            try:
                # unfollows non follower.
                self.api.destroy_friendship(f)
                total_followed += 1
                if total_followed % 10 == 0:
                    print(str(total_followed) + ' unfollowed so far.')
                if total_followed==self.max_unfollow:
                    print('unfollowed', max_unfollow,'users, now exiting it')
                    exit()

                print('Unfollowed user. Sleeping 15 seconds.')
                sleep(15)
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                self.error_handling(e)
        print(total_followed)
        print('Mission >unfollowing the traitors< is completed.')
        print('You now have', len(set(self.followers)), 'followers')
        print('You follow', len(set(self.following)), 'ppl')
        
    def follow_back_who_follow_me(self):     #origine puis personnalisé
        # function to follow users that follow me.
        print('Starting to follow users...')
        # makes a new list of users who follow me and I don't.
        non_mutuals = set(self.followers) - set(self.following)
        total_followed = 0
        for f in non_mutuals:
            try:
                # follows follower
                self.api.create_friendship(f)
                total_followed += 1
                if total_followed % 10 == 0:
                    print(str(total_followed) + ' followed so far.')
                if total_followed==self.max_follow:
                    print('followed', max_follow, 'users, now exiting it')
                    exit()
                rand_n = randint(-10,10)/10 + 5
                print('Followed user', self.api.get_user(f).screen_name,' Sleeping', rand_n,'seconds.')
                sleep(rand_n)
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                self.error_handling(e)
        print("Mission completed. Ppl followed:", total_followed)
        #print("Ppl following me:", len(set(self.followers)))
        #print("Ppl I follow:", len(set(self.following)))
    
    def searchFBTweet(self):                    #personnalisé
        #search follow back tweet
        results = self.api.search(q = keywords, result_type = "recent", count = 200)
        id_str_list = list()
        screen_name_list = list()
        for tweet in results:
            try:
                if hasattr(tweet, 'retweeted_status'): #the search has found a RT of the wanted tweet
                    #check the date of the wanted tweet
                    date_RT = tweet.created_at
                    date_wanted_tweet = tweet.retweeted_status.created_at
                    time_elapsed = date_RT - date_wanted_tweet
                    if time_elapsed < timedelta(seconds = 24*60*60):
                        #keep the result if RT was made less than one day after the tweet
                        if not tweet.retweeted_status.id_str in id_str_list:
                            id_str_list.append(tweet.retweeted_status.id_str)
                            screen_name_list.append(tweet.retweeted_status.user.screen_name)
                            print('Tweet appended from a RT made after', time_elapsed)
                    else:
                        print('Tweet rejected from a RT made after', time_elapsed)                        
                else:
                    time_elapsed = datetime.now() - tweet.created_at
                    if not tweet.id_str in id_str_list:
                        id_str_list.append(tweet.id_str)
                        screen_name_list.append(tweet.user.screen_name)
                        print('Original tweet appended made', time_elapsed, 'ago.')
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                self.error_handling(e)
        print('Found', len(id_str_list), '(', len(screen_name_list), ') valid tweets')
        return (id_str_list, screen_name_list)
    
    def searchAndFavReplies(self, id_str_list, screen_name_list):
        #search replies to posts
        faved_comments_all = 0
        for i in range(0, len(id_str_list)-1):
            faved_comments = 0
            try:
                replies = self.api.search(q = screen_name_list[i], since_id = id_str_list[i])
                for reply in replies:
                    if reply.in_reply_to_status_id_str == id_str_list[i]:
                        self.api.create_favorite(id = reply.id_str)
                        faved_comments += 1
                        rand_n = 1 + randint(0, 20)/10
                        print("Faved a comment. Sleeping", rand_n, "seconds")
                        sleep(rand_n)                    
            except (tweepy.RateLimitError, tweepy.TweepError) as e:
                self.error_handling(e)
            print('Faved', faved_comments, 'on this tweet')
            faved_comments_all += faved_comments
        print('Mission completed. Faved', faved_comments_all, 'comments')

    @staticmethod
    def error_handling(e):
        error = type(e)
        if error == tweepy.RateLimitError:
            print("You've hit a limit! Sleeping for 30 minutes.")
            sleep(60 * 30)
        elif error == tweepy.TweepError:
            print('Uh oh. Could not complete task. Sleeping 10 seconds.')
            sleep(10)
        else:
            print('Uh oh. Could not get exception type. Sleeping 10 minutes.')
            sleep(60*10)

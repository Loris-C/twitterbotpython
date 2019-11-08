# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 12:28:19 2019

@author: camoinlor
"""


#=== MORNING ROUTINE ===

from myFirstTwitterBot import TwitterBot
from time import sleep
#Fire ppl I follow who do not follow me anymore
#TB.unfollow_back_who_not_follow_me()

#First salve of likes on replies on FB tweets

for i in range(1,200):
    sleep(60*20)
    (id_str_list, screen_name_list) = TwitterBot().searchFBTweet()
    TwitterBot().searchAndFavReplies(id_str_list, screen_name_list)
    TwitterBot().follow_back_who_follow_me()
    print('== Round finished. Now sleeping 20 minutes before another one ==')
    sleep(60*5)
    TwitterBot().follow_back_who_follow_me()
    sleep(60*5)
    TwitterBot().follow_back_who_follow_me()
    if i%5 == 0:
        print("5 rounds have been done. Let's check who are the traitors")
        TwitterBot().unfollow_back_who_not_follow_me()
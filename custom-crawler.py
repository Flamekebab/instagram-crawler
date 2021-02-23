#!/usr/bin/env python3
# Vague plan for this program - use rotating proxies (from luminati.io or equivalent) to query a particular profile
# This will give a nice pile of information. That can then be filtered through to find other notable accounts.
# Run this on those, possibly tweaked based on W's parameters.

# Notes:
# The instaclient python library was... well, not well documented. Instead we're using Instaloader which seems to be much
# more mature.
#
# It seems that Instagram outputs JSON if a profile is accessed with the /?__a=1 parameter
# For example: https://www.instagram.com/flamekebab/?__a=1

import csv
import sys
import json
import string
import requests
from requests.auth import HTTPBasicAuth 
from typing import List
import re
from pathlib import Path
#Python doesn't have PHP's var_dump. Fortunately someone wrote an equivalent so we have it here for debugging:
from var_dump import var_dump

import instaloader

# Get instance
L = instaloader.Instaloader()

# Optionally, login or load session
L.login("username", "password")        # (login)
# L.interactive_login("username")      # (ask password on terminal)
# L.load_session_from_file("username") # (load session created w/
#                                #  `instaloader -l USERNAME`)

#Who are we stalking today?
username = "Flamekebab"

#We're going to find info about their followers and log the relevant bits of info. 
#This might take multiple attempts so we need to save stuff
#Let's keep adding to our file or create it if it doesn't exist
jsonPath = "./" + username + "_followers.json"


#Check if the file exists already
resultsFile = Path(jsonPath)
if resultsFile.is_file():
    # file exists
    with open(jsonPath, 'r') as infile:
            followerList = json.load(infile)
else:
    followerList = []
    with open(jsonPath, 'w') as outfile:
            json.dump(followerList, outfile)



#Now we can load up their profile and get started
profile = instaloader.Profile.from_username(L.context, username)
var_dump(profile.business_category_name)

follower_iterator = profile.get_followers()

resumeFile = Path("./resume_information.json")
if resumeFile.is_file():
    follower_iterator.thaw(load(resumeFile))

#follower_iterator is a NodeIterator object that's something to do with GraphQL, something that underpins Instagram I assume
try:
    for follower in follower_iterator:
        followerInfo = {}
        #As per Wayne's chosen columns:
        followerInfo['username'] = follower.username
        followerInfo['full_name'] = follower.full_name
        followerInfo['is_private'] = follower.is_private
        followerInfo['external_url'] = follower.external_url
        followerInfo['posts'] = follower.mediacount
        followerInfo['followers'] = follower.followers
        followerInfo['following'] = follower.followees
        followerInfo['bio'] = follower.biography
        #This one is a boolean:
        followerInfo['business_account'] = follower.is_business_account
        #I don't know how this one will work yet:
        followerInfo['business_category'] = follower.business_category_name
        followerList.append(followerInfo)
        
        #var_dump(followerInfo)
except KeyboardInterrupt:
    #Pause the function and save the current iterator
    #save("./resume_information.json", follower_iterator.freeze())
    save_structure_to_file()
    
    # resumePath = "./resume_information.json"
    # with open(resumePath, 'w') as outfile:
    #         json.dump(follower_iterator.freeze(), outfile)
    #Save the followers we've gathered the data on
    with open(jsonPath, 'w') as outfile:
            json.dump(followerList, outfile)

                
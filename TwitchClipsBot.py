#############################################
# Author: Sean Coakley
#############################################
# to use this script, you must get both twitch and twitter api authentication.
# when that is done, replace the variables below with your information.
# if you want this script to repeat at set times, it is recommended to set up a scheduled task through your OS.


# Twitch Info
twitch_client_id = "replace with your twich client id"
twitch_secret = "replace with your twich secret"
game_id = 0 # replace this 0 with the twitch game id of your game of interest

# Twitter Info
twitter_consumer_key = 'replace with your twitter consumer key'
twitter_consumer_secret = 'replace with your twitter consumer secret'
twitter_bearer_token = 'replace with your twitter bearer token'
twitter_access_token = 'replace with your twitter access token secret'
twitter_access_token_secret = 'replace with your twitte access token secret'

#############################################

import datetime
from twitchAPI.twitch import Twitch
import os
import sys
import urllib.request
import tweepy

# Clip variables
clip_url = ""
clip_title = ""
clip_streamer = ""
clip_id = ""
basepath = 'tmp/'       # directory that videos will be saved to
clip_to_post = {}

# helper function
def dl_progress(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r...%d%%" % percent)
    sys.stdout.flush()

# Begin the script
print("Bot initiated. Waiting to run code.")


# Get Twitch Clips
#############################################

# get clips
twitch = Twitch(twitch_client_id, twitch_secret)

# find the top 10 clips of the week
clips = twitch.get_clips(game_id=game_id, started_at=datetime.datetime.now()-datetime.timedelta(days=7), first=10)['data']

# get_clips should already return a sorted list, but if you want to combine multiple clip lists then this will be necessary
def clipSort(mydict):
    return mydict['view_count']
clips.sort(reverse=True, key=clipSort)

print(f"{len(clips)} clips retrieved")


# Find Most Viewed Clip Not Already Posted
#############################################

new_top_clip = 0 # index of the most viewed clip that hasn't been posted before
clip_file = 'clip_list.txt' # this file contains a list of clip id's that have already been posted

with open(clip_file, 'r') as file:    # find most viewed not posted clip
    lines = file.readlines()
    read = True
    while read == True:
        read = False
        for line in lines:
            if clips[new_top_clip]['id'].rstrip() == line.rstrip():
                new_top_clip += 1
                read = True
    clip_to_post = clips[new_top_clip]
with open(clip_file, 'a') as file:
    file.writelines(clip_to_post['id'].rstrip() + '\n')

# clip info
clip_url = clip_to_post['url']
clip_title = clip_to_post['title']
clip_streamer = clip_to_post['broadcaster_name']
clip_id = clip_to_post['id']
# clip_views = clip_to_post['views']
print('Clip of choice found')


# Download Clip MP4
#############################################

clip_info = twitch.get_clips(clip_id=clip_id)

thumb_url = clip_info['data'][0]['thumbnail_url']
mp4_url = thumb_url.split("-preview",1)[0] + ".mp4"
out_filename = clip_id + ".mp4"
output_path = (basepath + out_filename)

# create the basepath directory where videos are saved
if not os.path.exists(basepath):
    os.makedirs(basepath)

try:
    urllib.request.urlretrieve(mp4_url, output_path, reporthook=dl_progress)
except:
    print("An exception occurred")

print('\nVideo saved to files')


# Post Tweet
#############################################

auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)
api = tweepy.API(auth)
client = tweepy.Client(consumer_key=twitter_consumer_key, consumer_secret=twitter_consumer_secret, access_token=twitter_access_token, access_token_secret=twitter_access_token_secret, bearer_token=twitter_bearer_token)

print('Posting tweet...')
status = f'{clip_title}\n\n~{clip_streamer}'
vid_filename=f'{basepath}{clip_id}.mp4'
video = [api.media_upload(filename=vid_filename, chunked=True, media_category="tweet_video").media_id]

client.create_tweet(text=status, media_ids=video)
print('New Tweet Made :)')


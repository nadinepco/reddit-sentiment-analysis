##########################################################################
##########################################################################
                    # REDDIT POST COLLECTOR #
##########################################################################
##########################################################################


# load packages
from pymongo import MongoClient
from faker import Faker
from requests.auth import HTTPBasicAuth
from datetime import datetime
import requests
import time
import logging
import random
import os
import re



##########################################################################
                    # COLLECT REDDIT POSTS #
##########################################################################

##########################################################################
                    # START: DEFINE FUNCTIONS #
##########################################################################
def mongodb_collection():
    """
    connects to mongodb and creates posts collection in reddit database
    """
    # establish connection to mongodb container
    client = MongoClient(
        host="mongodb",   # host: name of the container
        port=27017        # port: port inside the container
        )

    # create twitter database
    db = client.reddit
    # equivalent of CREATE DATABASE reddit;

    # define the collection
    collection = db.posts
    # equivalent of CREATE TABLE posts;

    return collection

def get_token_access():
    '''
    Gets temporary access token from reddit by using the authentication information found in the .env file.
    :returns: header with access token type and access token
    '''
    # prepare authentication information for requesting a temporary access token
    basic_auth = HTTPBasicAuth(
        username=os.getenv('CLIENT_ID'), # the client id
        password=os.getenv('SECRET')   # the secret
    )
    print(basic_auth.username)

    GRANT_INFORMATION = dict(
        grant_type="password",
        username=os.getenv('USERNAME'), # REDDIT USERNAME
        password=os.getenv('PASSWORD') # REDDIT PASSWORD
    )
    #logging.DEBUG(f'GRANT_INFORMATION:{str(GRANT_INFORMATION)}')

    headers = {
        'User-Agent': 'week06_project'
    }

    ### POST REQUEST FOR ACCESS TOKEN
    POST_URL = "https://www.reddit.com/api/v1/access_token"

    access_post_response = requests.post(
        url=POST_URL,
        headers=headers,
        data=GRANT_INFORMATION,
        auth=basic_auth
    ).json()

    # Print the Bearer Token sent by the API
    print(f"access_post_response: {access_post_response}" )

    headers['Authorization'] = access_post_response['token_type'] + ' ' + access_post_response['access_token']

    print(f"headers: {headers}")
    return headers


def get_reddit_posts(topic, headers):
    '''
    Send a get request to download the latest (new) subreddits.
    :param topic: topic in reddit
    :param headers: header to send in the request. This should include the access token.
    :return full_response: contents from the response 
    '''

    URL = f"https://oauth.reddit.com/r/{topic}/new"  # You could also select ".../hot" to fetch the most popular posts.
    
    response = requests.get(
    url=URL,
    headers=headers  # this request would not work without the access token 
    ).json()

    # get the contents fromt the key data and dict children
    full_response = response['data']['children']
    return full_response

def truncate_post(post):
    # define the pattern to match a sentence
    sentence_pattern = r'(?<=[.?!])\s+'
    
    # text = post['text']
    # dplit the text into sentences using the pattern
    sentences = re.split(sentence_pattern, post)
    
    # Extract the first three sentences and join them back into a truncated text
    truncated_post = ' '.join(sentences[:2])
    logging.debug(f'truncated_post:{truncated_post}')
    return truncated_post

def insert_posts(full_response):
    '''
    Insert posts to mongodb
    :param full_response: 
    '''
    post_number = 1
    # Go through the full response and define a mongo_input dict
    for post in full_response:
        # truncate the actual content
        text_post = truncate_post(post['data']['selftext'])
        logging.warning(f"\n-----text_post: {text_post} -----\n")
        # get the reddit post
        reddit_post = {
            'id' : post['data']['id'],
            'subreddit_id' : post['data']['subreddit_id'],
            'time' : datetime.fromtimestamp(post['data']['created_utc']).strftime('%Y-%m-%d %H:%M:%S'),
            'title' : post['data']['title'],
            'text' : text_post
        }

        # insert the post into the collection
        COLLECTION.insert_one(reddit_post) 
        logging.warning(f"\n-----reddit posts {post_number} already inserted into MongoDB-----\n")
        post_number += 1
        time.sleep(1)

##########################################################################
                    # END: DEFINE FUNCTIONS #
##########################################################################


# define the collection
COLLECTION = mongodb_collection()

headers = get_token_access()
topic = 'Berlin'
full_response = get_reddit_posts(topic, headers)
insert_posts(full_response)


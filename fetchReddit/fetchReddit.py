import praw
import ctypes
try:
	import configparser
except:
	import ConfigParser
import urllib.request as dl
import os
import mimetypes
import sys
import requests
import json

from flask import Flask, render_template, redirect, url_for,request
from flask import make_response
app = Flask(__name__,instance_relative_config=True)

lastImage = 0
reddit = praw.Reddit('bot1')
config = configparser.ConfigParser()
source = ''
#commandDict = {'fetch': getImages, 'next': setDesktop}
@app.route('/')
@app.route('/index')
def main():
    # Configuration
    config.read('config.ini')

    # Create image directory if it doesnt exist
    # if not os.path.exists(config['Bot']['downloaddirectory']):
    #    os.makedirs(config['Bot']['downloaddirectory'])

    print('fetchReddit ready')

@app.route('/getImages', methods=['GET'])
def getImages():      #fetches images
    #os.chdir(config['Bot']['downloadDirectory'])
    source = parseSources()
    print('Downloading from subreddits: ' + source)
    errorCount = 0
    subreddit = reddit.subreddit(source)
    images = []
    for submission in subreddit.top('month', limit=int(config['Bot']['maxImages'])):
        #print('Input: ' + submission.title + " at " + submission.url)
        try:
            # If the url does not indicate it contains an image, raise an IOError
            mimetype = mimetypes.guess_type(submission.url)[0]
            if not (mimetype and mimetype.startswith('image')):
                raise IOError

            images.append(submission.url)
            """
            #Downloads the image (removed, place image url in json file instead)
            dl.urlretrieve(submission.url, str(imgName) + '.png', reporthook=progressDisplay)
            errorCount = 0
            print('\n')
            print('Searching for highest resolution image for ' + submission.title + '.png')
            reverseSearchImage(imgName)
            print('\n')
            imgName += 1
            """

        # Catch error if url fails
        except IOError:
            if errorCount < 30:
                print('No image detected, skipping')
                errorCount += 1
            else:
                print('No image posts found in 30 tries, make sure to include only image subredddits in config.ini. Terminating...')
                os.chdir('..')
                break
    #Exporting images array
    output = {'images':images}
    with open(config['Bot']['imageOutput'], 'w') as outfile:
        json.dump(output, outfile)

def parseSources():
    # Creates a string representing all subreddits in config.ini
    source = ''
    subNum = 0
    while str(subNum) in config['Sources']:
        source += config['Sources'][str(subNum)]
        subNum += 1
        if str(subNum) in config['Sources']:
            source += '+'
    return source

if __name__ == '__main__':
    main()
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

lastImage = 0
reddit = praw.Reddit('bot1')
config = configparser.ConfigParser()
#commandDict = {'fetch': getImages, 'next': setDesktop}


def main():
    # Configuration
    config.read('config.ini')

    # Create image directory if it doesnt exist
    if not os.path.exists(config['Bot']['downloaddirectory']):
        os.makedirs(config['Bot']['downloaddirectory'])

    print('wpbot ready')
    #getInput()
    getImages()


#def getInput():
    # Acts as user interface, gets user input and runs appropriate functions
#    print('Type next to fetch to fetch images, and help for more information')
#    while True:
#        command = input('')
#        if (command == 'fetch'):
#            getImages()
#        elif (command == 'next'):
#            setDesktop()
#        elif (command.split()[0] == 'set'):
#            set(command.split()[1])


def getImages():
    os.chdir(config['Bot']['downloadDirectory'])
    source = parseSources()
    print('Downloading from subreddits: ' + source)
    imgName = 0
    errorCount = 0
    subreddit = reddit.subreddit(source)
    for submission in subreddit.top('month', limit=int(config['Bot']['maxImages'])):
        print('Downloading --- ' + submission.title)
        print(submission.url)
        try:
            # If the url does not indicate it contains an image, raise an IOError
            mimetype = mimetypes.guess_type(submission.url)[0]
            if not (mimetype and mimetype.startswith('image')):
                raise IOError

            dl.urlretrieve(submission.url, 'img_' + str(imgName) + '.jpg', reporthook=progressDisplay)
            errorCount = 0
            imgName += 1

        # Catch error if url fails
        except IOError:
            if errorCount < 30:
                print('No image detected, skipping')
                errorCount += 1
            else:
                print('No image posts found in 30 tries, make sure to include only image subredddits in config.ini. Terminating...')
                os.chdir('..')
                break
    os.chdir('..')
    print('Downloading complete!')


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

def progressDisplay(count, block_size, total_size):
	percent = min(100,int(count * block_size * 100 / total_size))
	sys.stdout.write('\r...%d%%' % percent)
	sys.stdout.flush()


if __name__ == '__main__':
    main()

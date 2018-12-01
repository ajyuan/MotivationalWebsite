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
    getInput()


def getInput():
    # Acts as user interface, gets user input and runs appropriate functions
    print('Type next to fetch to fetch images, and help for more information')
    while True:
        command = input('')
        if (command == 'fetch'):
            getImages()
        elif (command == 'next'):
            setDesktop()
        elif (command.split()[0] == 'set'):
            set(command.split()[1])


def reverseSearchImage(img):
    searchUrl = 'http://www.google.hr/searchbyimage/upload'
    multipart = {'encoded_image': (str(img)+'.png', open(str(img)+'.png', 'rb')), 'image_content': ''}
    response = requests.post(searchUrl, files=multipart, allow_redirects=False)
    fetchUrl = response.headers['Location']
    print('The highest resolution image was found at ' + fetchUrl)


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

            dl.urlretrieve(submission.url, str(imgName) + '.png', reporthook=progressDisplay)
            errorCount = 0
            print('\n')
            print('Searching for highest resolution image for ' + submission.title + '.png')
            reverseSearchImage(imgName)
            print('\n')
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


def set(img=0):
    if not os.path.isfile(str(img) + '.png'):
        print('Error: Background ' + str(img) + ' not found in ' + os.getcwd() + ', please use range 0 to ' + str(int(config['Bot']['maximages'])-1))
        return
    
    print('Setting wallpaper to ' + str(img))

    config['Bot']['currentWP'] = str(img)
    with open('config.ini', 'w') as configfile:    # save
        config.write(configfile)
    
    setDesktop()


def setDesktop():
    img = int(config['Bot']['currentWP'])
    # Selects the next image from imported images and calls setter method
    # Acts as a wrapper for setter that sets next image and catches exceptions
    output = img + 1
    try:
        if setter(img):
            print('Next background, now using background ' + str(img))
    except IOError:
        if (img == int(config['Bot']['maxImages'])-1):
            output = 0
            setter(0)
        else:
            if promptOverwrite('No backgrounds found, fetch backgrounds? (y/n)'):
                getImages()
            img = 0
            setter(img)
    config['Bot']['currentWP'] = str(output)
    with open('config.ini', 'w') as configfile:    # save
        config.write(configfile)


def setter(img=0):
    os.chdir(config['Bot']['downloadDirectory'])
    # Helper function for setDesktop that gets the appropriate image
    if not os.path.isfile(str(img) + '.png'):
        print('Error: Background ' + str(img) + ' not found in ' + os.getcwd())
        return False
    ctypes.windll.user32.SystemParametersInfoW(
        20, 0, str(img) + '.png', 3)
    os.chdir('..')
    return True


def promptOverwrite(prompt):
    while True:
        output = prompt(prompt)
        if output == 'y' or output == 'yes':
            return True
        elif output == 'n' or output == 'no':
            return False
        else:
            pass

def progressDisplay(count, block_size, total_size):
	percent = min(100,int(count * block_size * 100 / total_size))
	sys.stdout.write('\r...%d%%' % percent)
	sys.stdout.flush()


if __name__ == '__main__':
    main()

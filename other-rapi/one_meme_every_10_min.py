import requests
from bs4 import BeautifulSoup
import time

TOKEN = '6324200625:AAHTGk3y_51czqWHkByuRERPbIAyNZbfMpE'
url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'

def get_image():

    d = requests.get('https://www.reddit.com/r/memes/new/')
    s = BeautifulSoup(d.text, 'html.parser')

    try:
        a = s.find(id='post-image')
        w = requests.get(a['src'])
        return w.content

    except TypeError:

        a = s.find_all(class_='max-h-[100vw] h-full w-full object-contain relative')
        for _ in range(len(a)):
            link = a[_]['src']
            if link != None:
                break
        link = requests.get(link)
        return link.content

data = {'chat_id': '@meme_every_10_min'}
while True:
    file = {'photo': get_image()}
    send = requests.post(url, data=data, files=file)
    time.sleep(600)

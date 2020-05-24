from __init__ import MangaSource
import cfscrape
from bs4 import BeautifulSoup
import dateparser
import humanize
import datetime as dt

def Manganelo(MangaSource):
    source_name = 'Manganelo'
    source_id = 'mgnelo'

    upd_url = 'https://manganelo.com/'

    requests = cfscrape.Session()

    def updates(self, count=5):
        mgd = []
        soup = BeautifulSoup(requests.get(upd_url).text, features='html.parser')
        for x in soup.find_all('div', {'class': 'content-homepage-item'}, limit=count):
            title = x.find('a', {'class': 'tooltip item-img'})
            iden = title['href'].split('/')[-1]
            title = title['title']
            time = humanize.naturaltime(dt.datetime.now()-dateparser.parse(x.find('i').text))
            img = x.find('img', {'class': 'img-loading'})['src']
            mgd.append({
                'name': title,
                'cover': img,
                'time': time,
                'id': iden
            })
        pass

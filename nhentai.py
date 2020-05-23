from . import MangaSource
from bs4 import BeautifulSoup
import datetime as dt
import humanize
import cfscrape

class NHentai(MangaSource):
    source_name = 'NHentai'
    source_id = 'nhn'

    base_url = 'https://nhentai.net'
    top_url = 'https://nhentai.net/language/english/popular'
    upd_url = 'https://nhentai.net/language/english'

    requests = cfscrape.Session()

    def updates(self, count=5):
        mgd = []
        soup = BeautifulSoup(self.requests.get(self.upd_url).text, features='html.parser')
        for x in soup.find_all('div', {'class': 'gallery'}, limit=count):
            ft = BeautifulSoup(self.requests.get(self.base_url+x.find('a')['href']).text, features='html.parser').find('div', {'id': 'info'}).find('time')['datetime']
            mgd.append({
                'name': x.find('div', {'class': 'caption'}).text,
                'cover': x.find('img')['data-src'].replace('thumb', 'cover'),
                'id': x.find('a', {'class': 'cover'})['href'].split('/')[-2],
                'time': humanize.naturaltime(dt.datetime.now()-dt.datetime.strptime(ft, '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=None))
            })
        return mgd

    def top(self, count=5):
        mgd = []
        soup = BeautifulSoup(self.requests.get(self.upd_url).text, features='html.parser')
        for x in soup.find_all('div', {'class': 'gallery'}, limit=count):
            ft = BeautifulSoup(self.requests.get(self.base_url+x.find('a')['href']).text, features='html.parser').find('div', {'id': 'info'}).find('time')['datetime']
            mgd.append({
                'name': x.find('div', {'class': 'caption'}).text,
                'cover': x.find('img')['data-src'].replace('thumb', 'cover'),
                'id': x.find('a', {'class': 'cover'})['href'].split('/')[-2],
                'time': humanize.naturaltime(dt.datetime.now()-dt.datetime.strptime(ft, '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=None))
            })
        return mgd

    def manga(self, iden):
        try:
            mg_url = f'{self.base_url}/g/{iden}/'
            soup = BeautifulSoup(self.requests.get(mg_url).text, features='html.parser').find('section', {'id': 'tags'})
            genres = []
            for x in soup.find_all('span', {'class': 'tags'})[2].find_all('a'):
                x.span.decompose()
                genres.append(x.text.strip())
            authors = []
            for x in soup.find_all('span', {'class': 'tags'})[3].find_all('a'):
                x.span.decompose()
                authors.append(x.text.strip())
            authors = ', '.join(authors)
            dat = {
                'description': '',
                'author': authors,
                'chapters_number': 1,
                'genres': genres,
                'chapters': [{
                    'id': iden,
                    'title': 'READ NOW'
                }]
            }
            return {
                'status': 'ok', 
                'result': dat
            }
        except Exception as e:
            print(type(e), e, iden)
            return {
                'status': 'error'
        }

    def chapter(self, iden):
        try:
            mg_url = f'{self.base_url}/g/{iden}/'
            soup = BeautifulSoup(self.requests.get(mg_url).text, features='html.parser')
            pgs = []
            for x in soup.find_all('div', {'class': 'thumb-container'}):
                trurl = x.find('img')['data-src']
                trurl = trurl.replace('t.jpg', '.jpg')
                trurl = trurl.replace('https://t', 'https://i')
                pgs.append(trurl)
            return {
                'status': 'ok',
                'result': pgs
            }
        except Exception as e:
            print(type(e), e)
            return {
                'status': 'error'
            }

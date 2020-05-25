from . import MangaSource
import cfscrape
from bs4 import BeautifulSoup
import dateparser
import humanize
import datetime as dt

## TO BE FIXED (CLOUDFLARE ERROR 1020)
"""
class Manganelo(MangaSource):
    source_name = 'Manganelo'
    source_id = 'mgnelo'

    upd_url = 'https://manganelo.com/'
    top_url = 'https://manganelo.com/genre-all?type=topview'
    mg_url = 'https://manganelo.com/manga/{}'
    chp_url = 'https://manganelo.com/chapter/{}/{}'

    requests = cfscrape.Session()

    def updates(self, count=5):
        mgd = []
        soup = BeautifulSoup(self.requests.get(self.upd_url).text, features='html.parser')
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
        return mgd

    def top(self, count=5):
        mgd = []
        soup = BeautifulSoup(self.requests.get(self.top_url).text, features='html.parser')
        for x in soup.find_all('div', {'class': 'content-genres-item'}, limit=count):
            title = x.find('a', {'class': 'genres-item-name text-nowrap a-h'})
            iden = title['href'].split('/')[-1]
            title = title['title']
            time = humanize.naturaltime(dt.datetime.now()-dateparser.parse(x.find('span', {'class': 'genres-item-time'}).text))
            img = x.find('img', {'class': 'img-loading'})['src']
            mgd.append({
                'name': title,
                'cover': img,
                'time': time,
                'id': iden
            })
        return mgd

    def manga(self, iden):
        try:
            url = self.mg_url.format(iden)
            soup = BeautifulSoup(self.requests.get(url).text, features='html.parser')
            print(soup)
            chs = [{
                    'id': iden+';'+y.find('a')['href'].split('/')[-1],
                    'title': y.find('a').text
                } for y in soup.find('ul', {'class': 'row-content-chapter'}).find_all('li')]
            desc = soup.find('div', {'class': 'panel-story-info-description'})
            desc.h3.decompose()
            meta = soup.find('table', {'class': 'variations-tableInfo'}).find_all('tr')
            dat = {
                'description': desc.text.strip(),
                'author': ', '.join([x.text for x in meta[1].find('td', {'class': 'table-value'}).find_all('a')]),
                'chapters_number': len(chs),
                'genres': [x.text for x in meta[3].find('td', {'class': 'table-value'}).find_all('a')],
                'chapters': chs
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
            mg, chp = iden.split(';')
            url = self.chp_url.format(mg, chp)
            soup = BeautifulSoup(self.requests.get(url).text, features='html.parser')
            return {
                'status': 'ok',
                'result': [x['src'] for x in soup.find('div', {'class': 'container-chapter-reader'}).find_all('img')]
            }
        except Exception as e:
            print(type(e), e)
            return {
                'status': 'error'
            }
"""
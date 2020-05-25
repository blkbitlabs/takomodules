from . import MangaSource
import cfscrape
from bs4 import BeautifulSoup

class ManhuaPlus(MangaSource):
    source_name = 'ManhuaPlus'
    source_id = 'mhpl'

    base_url = 'https://manhuaplus.com/'
    top_url = 'https://manhuaplus.com/hot/'
    mg_url = 'https://manhuaplus.com/comics/{}/'
    chp_url = 'https://manhuaplus.com/chapter/{}/'

    requests = cfscrape.create_scraper()
    
    def updates(self, count=5):
        mgd = []
        soup = BeautifulSoup(self.requests.get(self.base_url).text, parser='html.parser').find('div', {'class': 'items'})
        for x in soup.find_all('div', {'class': 'item'}, limit=count):
            img = x.find('img')['data-original']
            title = x.find('a')
            iden = title['href'].split('/')[-2]
            title = title['title']
            time = x.find('i', {'class': 'time'}).text
            mgd.append({
                'name': title,
                'id': iden,
                'cover': img,
                'time': time
            })
        return mgd

    def top(self, count=5):
        mgd = []
        soup = BeautifulSoup(self.requests.get(self.top_url).text, parser='html.parser').find('div', {'class': 'items'})
        for x in soup.find_all('div', {'class': 'item'}, limit=count):
            img = x.find('img')['data-original']
            title = x.find('a')
            iden = title['href'].split('/')[-2]
            title = title['title']
            time = x.find('i', {'class': 'time'}).text
            mgd.append({
                'name': title,
                'id': iden,
                'cover': img,
                'time': time
            })
        return mgd

    def manga(self, iden):
        try:
            soup = BeautifulSoup(self.requests.get(self.mg_url.format(iden)).text, features='html.parser')
            chs = [{
                'id': x.find('a')['href'].split('/')[-2],
                'title': x.find('a').text
            } for x in soup.find('div', {'class': 'list-chapter'}).find('ul').find_all('li', {'class': 'row'})[1:]]
            dat = {
                'description': soup.find('p', {'class': 'shortened'}).text,
                'author': soup.find('li', {'class': 'author'}).find_all('p')[-1].text,
                'chapters_number': len(chs),
                'chapters': chs,
                'genres': [x.text for x in soup.find('li', {'class': 'kind'}).find_all('a')]
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
            url = self.chp_url.format(iden)
            pgs = BeautifulSoup(self.requests.get(url).text, features='html.parser').find('ul', {'class': 'blocks-gallery-grid'})
            pgs = [x.find('img')['src'] for x in pgs.find_all('li')]
            return {
                'status': 'ok', 
                'result': pgs
            }
        except Exception as e:
            print(type(e), e, iden)
            return {
                'status': 'error'
        }
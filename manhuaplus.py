from . import MangaSource
import cfscrape
from bs4 import BeautifulSoup
import dateparser
import datetime as dt
import humanize

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
        soup = BeautifulSoup(self.requests.get(self.base_url).text, features='html.parser').find('div', {'class': 'items'})
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
        soup = BeautifulSoup(self.requests.get(self.top_url).text, features='html.parser').find('div', {'class': 'items'})
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

class Manga347(MangaSource):
    source_name = 'Manga347'
    source_id = 'mg347'

    base_url = 'https://manga347.com/'
    mg_url = 'https://manga347.com/manga/{}/'
    chp_url = 'https://manga347.com/manga/{}/{}/'
    adm_ajax = 'https://manga347.com/wp-admin/admin-ajax.php'

    requests = cfscrape.create_scraper()
    
    def updates(self, count=5):
        mgd = []
        soup = BeautifulSoup(self.requests.get(self.base_url).text, features='html.parser').find('div', {'class': 'page-content-listing'})
        for x in soup.find_all('div', {'class': 'page-item-detail'}, limit=count):
            img = 'https'+x.find('img')['data-src'].split('https')[-1].replace('175x238', '')
            title = x.find('a')
            chid = x.find('div', {'data-post-id': True})['data-post-id']
            iden = title['href'].split('/')[-2]
            time = BeautifulSoup(self.requests.post(self.adm_ajax, data={'action': 'manga_get_chapters', 'manga': chid}).text, features='html.parser').find('li', {'class': 'wp-manga-chapter'}).find('span')
            title = title['title']
            try:
                time = time.find('i').text
            except:
                time = time.find('a')['title']
            mgd.append({
                'name': title,
                'id': iden,
                'cover': img,
                'time': time
            })
        return mgd

    def top(self, count=5):
        # Does not have top
        return self.updates(count)

    def manga(self, iden):
        try:
            soup = BeautifulSoup(self.requests.get(self.mg_url.format(iden)).text, features='html.parser')
            chid = soup.find('div', {'id': 'manga-chapters-holder'})['data-id']
            chid = BeautifulSoup(self.requests.post(self.adm_ajax, data={'action': 'manga_get_chapters', 'manga': chid}).text, features='html.parser').find_all('li', {'class': 'wp-manga-chapter'})
            chs = [{
                'id': iden+';'+x.find('a')['href'].split('/')[-2],
                'title': x.find('a').text.strip()
            } for x in chid]
            dat = {
                'description': soup.find('div', {'class': 'summary__content'}).text,
                'author': soup.find('div', {'class': 'author-content'}).text,
                'chapters_number': len(chs),
                'chapters': chs,
                'genres': [x.text for x in soup.find('div', {'class': 'genres-content'}).find_all('a')]
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

class ManhuaUS(MangaSource):
    source_name = 'ManhuaUS'
    source_id = 'mhus'

    base_url = 'https://manhuaus.com/'
    mg_url = 'https://manhuaus.com/manga/{}/'
    chp_url = 'https://manhuaus.com/manga/{}/{}/'
    adm_ajax = 'https://manhuaus.com/wp-admin/admin-ajax.php'

    requests = cfscrape.create_scraper()
    
    def updates(self, count=5):
        mgd = []
        soup = BeautifulSoup(self.requests.get(self.base_url).text, features='html.parser').find('div', {'class': 'page-content-listing'})
        for x in soup.find_all('div', {'class': 'page-item-detail'}, limit=count):
            img = 'https'+x.find('img')['data-src'].split('https')[-1].replace('175x238', '')
            title = x.find('a')
            iden = title['href'].split('/')[-2]
            time = x.find('span', {'class': 'post-on'})
            title = title['title']
            try:
                time = time.find('a')['title']
            except:
                time = humanize.naturaltime(dt.datetime.now()-dateparser.parse(time.text))
            mgd.append({
                'name': title,
                'id': iden,
                'cover': img,
                'time': time
            })
        return mgd

    def top(self, count=5):
        # Does not have top
        return self.updates(count)

    def manga(self, iden):
        try:
            soup = BeautifulSoup(self.requests.get(self.mg_url.format(iden)).text, features='html.parser')
            chid = soup.find('div', {'class': 'listing-chapters_wrap'}).find_all('li', {'class': 'wp-manga-chapter'})
            chs = [{
                'id': iden+';'+x.find('a')['href'].split('/')[-1],
                'title': x.find('a').text.strip().capitalize()
            } for x in chid]
            dat = {
                'description': soup.find('div', {'class': 'summary__content'}).text,
                'author': soup.find('div', {'class': 'author-content'}).text,
                'chapters_number': len(chs),
                'chapters': chs,
                'genres': [x.text for x in soup.find('div', {'class': 'genres-content'}).find_all('a')]
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
            pgs = BeautifulSoup(self.requests.get(url).text, features='html.parser').find('ul', {'class': 'blocks-gallery-grid'})
            pgs = [x.find('img')['src'] for x in pgs.find_all('li') if x.figure is not None]
            return {
                'status': 'ok', 
                'result': pgs
            }
        except Exception as e:
            print(type(e), e, iden)
            return {
                'status': 'error'
        }
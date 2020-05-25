from . import MangaSource
import cfscrape
import concurrent.futures
from bs4 import BeautifulSoup
import datetime as dt
import dateparser
from urllib.parse import urlsplit, parse_qs
import humanize
import base64

class WEBTOONS(MangaSource):
    source_name = 'WEBTOONS'
    source_id = 'wbtns'

    base_url = 'https://www.webtoons.com'
    upd_url = 'https://www.webtoons.com/en/dailySchedule?sortOrder=UPDATE&webtoonCompleteType=ONGOING'
    top_url = 'https://www.webtoons.com/en/top'
    mg_url = 'https://m.webtoons.com/x/x/x/list?title_no={}'
    chp_url = 'https://www.webtoons.com/x/x/x/x/viewer?title_no={}&episode_no={}'
    mheaders = {
        'referer': 'https://m.webtoons.com'
    }
    requests = cfscrape.Session()

    def _reupload(self, url):
        dat = self.requests.get(url, headers=self.mheaders).content
        b = base64.b64encode(dat).decode("utf-8")
        upl = self.requests.post('https://api.imgbb.com/1/upload', data={'image': b, 'key': '14b5abc792a977027d12ed0f8370075d'}).json()
        return upl['data']['url']

    def updates(self, count=5):
        mgd = []
        soup = BeautifulSoup(self.requests.get(self.upd_url).text, features='html.parser')
        wkd = '_list_'+dt.datetime.today().strftime("%A").upper()
        soup = soup.find('div', {'class': wkd}).find('ul', {'class': 'daily_card'})
        for x in soup.find_all('li'):
            if len(mgd) < count and x.find('p', {'class': 'icon_area'}).text == 'UP':
                title = x.find('p', {'class': 'subj'}).text
                img = x.find('img')['src'].split('?')[0]+'type=q90'
                iden = parse_qs(urlsplit(x.find('a')['href']).query)['title_no'][0]
                time = BeautifulSoup(self.requests.get(self.mg_url.format(iden), headers=self.mheaders).text, features='html.parser').find('ul', {'id': '_episodeList'}).find_all('li', {'data-episode-no': True})[0].find('p', {'class': 'date'})
                try:
                    time.span.decompose()
                except:
                    pass
                time = humanize.naturaltime(dt.datetime.now()-dateparser.parse(time.text))
                mgd.append({
                    'name': title,
                    'id': iden,
                    'cover': img,
                    'time': time
                })
        return mgd

    def top(self, count=5):
        mgd = []
        soup = BeautifulSoup(self.requests.get(self.top_url).text, features='html.parser')
        for x in soup.find('ul', {'class': 'lst_type1'}).find_all('li', limit=count):
            title = x.find('p', {'class': 'subj'}).text
            img = x.find('img')['src'].split('?')[0]+'type=q90'
            iden = parse_qs(urlsplit(x.find('a')['href']).query)['title_no'][0]
            time = BeautifulSoup(self.requests.get(self.mg_url.format(iden), headers=self.mheaders).text, features='html.parser').find('ul', {'id': '_episodeList'}).find_all('li', {'data-episode-no': True})[0].find('p', {'class': 'date'})
            try:
                time.span.decompose()
            except:
                pass
            time = humanize.naturaltime(dt.datetime.now()-dateparser.parse(time.text))
            mgd.append({
                'name': title,
                'id': iden,
                'cover': img,
                'time': time
            })
        return mgd

    def manga(self, iden):
        try:
            soup = BeautifulSoup(self.requests.get(self.mg_url.format(iden), headers=self.mheaders).text, features='html.parser')
            chs = [{
                'id': iden+';'+x['data-episode-no'],
                'title': x.find('span', {'class': 'ellipsis'}).text
            } for x in soup.find('ul', {'id': '_episodeList'}).find_all('li', {'data-episode-no': True})]
            dat = {
                'description': soup.find('p', {'class': 'summary'}).text,
                'author': soup.find('p', {'class': 'author'}).text,
                'chapters_number': len(chs),
                'chapters': chs,
                'genres': [soup.find('p', {'class': 'genre'}).text]
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
            pgs = BeautifulSoup(self.requests.get(url).text, features='html.parser').find('div', {'id': '_imageList'})
            pool = concurrent.futures.ThreadPoolExecutor(8)
            pgs = [x['data-url'] for x in pgs.find_all('img')]
            futures = {pool.submit(self._reupload, (x)):i for i, x in enumerate(pgs)}
            pgs = [None]*len(pgs)
            for future in concurrent.futures.as_completed(futures):
                pgs[futures[future]] = future.result()

            return {
                'status': 'ok', 
                'result': pgs
            }
        except Exception as e:
            print(type(e), e, iden)
            return {
                'status': 'error'
        }
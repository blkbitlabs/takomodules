from . import MangaSource
import requests
from bs4 import BeautifulSoup
import dateparser
import datetime as dt
import humanize
import re
import json

class MangaEden(MangaSource):
    source_name = 'MangaEden'
    source_id = 'mgedn'

    base_url = 'https://www.mangaeden.com'
    top_url = 'https://www.mangaeden.com/en/en-directory/?order=1'
    upd_url = 'https://www.mangaeden.com/en/en-directory/?order=3'
    kitsu_manga = 'https://kitsu.io/api/edge/manga'
    kitsu_headers = {
                "Accept": "application/vnd.api+json",
                "Content-Type": "application/vnd.api+json"
    }
    auth_re = re.compile(r'/en/en-directory/\?author=(.+)')
    genre_re = re.compile(r'/en/en-directory/\?categoriesInc=(.+)')
    chapters_re = re.compile(r'var pages = (.+);')
    genres = {'School Life': '4e70e918c092255ef7001688', 'Sports': '4e70e91dc092255ef700172e', 'Mature': '4e70e91bc092255ef7001705', 'Mystery': '4e70e918c092255ef7001681', 'Comedy': '4e70e918c092255ef7001675', 'Action': '4e70e91bc092255ef70016f8', 'Romance': '4e70e918c092255ef7001677', 'Fantasy': '4e70e918c092255ef7001676', 'Webtoons': '4e70ea70c092255ef7006d9c', 'Tragedy': '4e70e918c092255ef7001672', 'Doujinshi': '4e70e928c092255ef7001a0a', 'Drama': '4e70e918c092255ef7001693', 'Ecchi': '4e70e91ec092255ef700175e', 'Supernatural': '4e70e918c092255ef700166a', 'Shounen': '4e70e918c092255ef700166f', 'Gender Bender': '4e70e921c092255ef700184b', 'Mecha': '4e70e922c092255ef7001877', 'Slice of Life': '4e70e918c092255ef700167e', 'Historical': '4e70e91ac092255ef70016d8', 'Adult': '4e70e92fc092255ef7001b94', 'Horror': '4e70e919c092255ef70016a8', 'Psychological': '4e70e919c092255ef70016a9', 'Harem': '4e70e91fc092255ef7001783', 'Sci-fi': '4e70e91bc092255ef7001706', 'One Shot': '4e70e91dc092255ef7001747', 'Seinen': '4e70e918c092255ef700168b', 'Yaoi': '4e70e91ac092255ef70016e5', 'Adventure': '4e70e918c092255ef700168e', 'Smut': '4e70e922c092255ef700185a', 'Shoujo': '4e70e918c092255ef7001667', 'Josei': '4e70e920c092255ef70017de', 'Martial Arts': '4e70e923c092255ef70018d0', 'Yuri': '4e70e92ac092255ef7001a57'}

    def updates(self, count=5):
        mgd = []
        soup = BeautifulSoup(requests.get(self.upd_url).text, features='html.parser')
        for x in soup.find('table', {'id': 'mangaList'}).find('tbody').find_all('tr'):
            if len(mgd) < 5:
                dat = [y for y in x.find_all('td')]
                title = dat[0].text.strip()
                mrl = dat[0].find('a')['href']
                time = dat[4].find('span').text
                img = BeautifulSoup(requests.get(self.base_url+mrl).text, features='html.parser')
                if img.find('img', {'alt': '404 NOT FOUND'}):
                    continue
                img = img.find('div', {'class': 'mangaImage2'})
                if img is None:
                    img = requests.get(self.kitsu_manga+f'?filter[text]={title}&page[limit]=1', headers=self.kitsu_headers).json()['data'][0]['attributes']['posterImage']['large']
                else:
                    img = 'https:'+img.find('img')['src']
                mgd.append({
                    'id': mrl.split('/')[-2],
                    'name': title,
                    'cover': img,
                    'time': humanize.naturaltime(dt.datetime.now()-dateparser.parse(time[3:]))
                })
            else:
                return mgd

    def top(self, count=5):
        mgd = []
        soup = BeautifulSoup(requests.get(self.top_url).text, features='html.parser')
        for x in soup.find('table', {'id': 'mangaList'}).find('tbody').find_all('tr'):
            if len(mgd) < count:
                dat = [y for y in x.find_all('td')]
                title = dat[0].text.strip()
                mrl = dat[0].find('a')['href']
                time = dat[4].find('span').text
                img = BeautifulSoup(requests.get(self.base_url+mrl).text, features='html.parser')
                if img.find('img', {'alt': '404 NOT FOUND'}):
                    continue
                img = img.find('div', {'class': 'mangaImage2'})
                if img is None:
                    img = requests.get(self.kitsu_manga+f'?filter[text]={title}&page[limit]=1', headers=self.kitsu_headers).json()['data'][0]['attributes']['posterImage']['large']
                else:
                    img = 'https:'+img.find('img')['src']
                mgd.append({
                    'id': mrl.split('/')[-2],
                    'name': title,
                    'cover': img,
                    'time': humanize.naturaltime(dt.datetime.now()-dateparser.parse(time[3:]))
                })
            else:
                return mgd

    def manga(self, iden):
        try:
            mg_url = self.base_url + '/en/en-manga/' + iden
            soup = BeautifulSoup(requests.get(mg_url).text, features='html.parser')
            chs = [{
                'id': iden+';'+x['id'][1:],
                'title': 'Ch. ' + x.find('b').text
            } for x in soup.find('table').find('tbody').find_all('tr')]
            dat = {
                'description': soup.find('h2', {'id': 'mangaDescription'}).text,
                'author': soup.find('a', {'href': self.auth_re}).text,
                'chapters_number': len(chs),
                'chapters': chs,
                'genres': [x.text for x in soup.find_all('a', {'href': self.genre_re})]
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
            chp_url = self.base_url + f'/en/en-manga/{mg}/{chp}/'
            pgs = self.chapters_re.search(requests.get(chp_url).text).group(1)
            dat = ['https:'+x['fs'] for x in json.loads(pgs)]
            return {
                'status': 'ok', 
                'result': dat
            }
        except Exception as e:
            print(type(e), e, iden)
            return {
                'status': 'error'
        }

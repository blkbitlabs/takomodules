from . import MangaSource
import datetime as dt
from bs4 import BeautifulSoup
import cfscrape, time, html, humanize, operator, re
from requests_futures.sessions import FuturesSession
from munch import munchify

class Mangadex(MangaSource):
    source_name = 'Mangadex'
    source_id = 'mgdx'

    update_url = 'https://mangadex.org/updates'
    api_url = 'https://mangadex.org/api'
    root_url = 'https://mangadex.org'
    genres = {1: '4-koma', 2: 'Action', 3: 'Adventure', 4: 'Award Winning', 5: 'Comedy', 6: 'Cooking', 7: 'Doujinshi', 8: 'Drama', 9: 'Ecchi', 10: 'Fantasy', 11: 'Gyaru', 12: 'Harem', 13: 'Historical', 14: 'Horror', 16: 'Martial Arts', 17: 'Mecha', 18: 'Medical', 19: 'Music', 20: 'Mystery', 21: 'Oneshot', 22: 'Psychological', 23: 'Romance', 24: 'School Life', 25: 'Sci-Fi', 28: 'Shoujo Ai', 30: 'Shounen Ai', 31: 'Slice of Life', 32: 'Smut', 33: 'Sports', 34: 'Supernatural', 35: 'Tragedy', 36: 'Long Strip', 37: 'Yaoi', 38: 'Yuri', 40: 'Video Games', 41: 'Isekai', 42: 'Adaptation', 43: 'Anthology', 44: 'Web Comic', 45: 'Full Color', 46: 'User Created', 47: 'Official Colored', 48: 'Fan Colored', 49: 'Gore', 50: 'Sexual Violence', 51: 'Crime', 52: 'Magical Girls', 53: 'Philosophical', 54: 'Superhero', 55: 'Thriller', 56: 'Wuxia', 57: 'Aliens', 58: 'Animals', 59: 'Crossdressing', 60: 'Demons', 61: 'Delinquents', 62: 'Genderswap', 63: 'Ghosts', 64: 'Monster Girls', 65: 'Loli', 66: 'Magic', 67: 'Military', 68: 'Monsters', 69: 'Ninja', 70: 'Office Workers', 71: 'Police', 72: 'Post-Apocalyptic', 73: 'Reincarnation', 74: 'Reverse Harem', 75: 'Samurai', 76: 'Shota', 77: 'Survival', 78: 'Time Travel', 79: 'Vampires', 80: 'Traditional Games', 81: 'Virtual Reality', 82: 'Zombies', 83: 'Incest'}
    requests = cfscrape.Session()
    session = FuturesSession(session=cfscrape.Session())

    def _manga(self, manga_id):
        data = {
            'type': 'manga',
            'id': manga_id
        }
        return self.session.get(self.api_url, params=data)

    def _chapter(self, chapter_id):
        data = {
            'id': chapter_id,
            'server': 'null',
            'type': 'chapter',
        }
        return self.session.get(self.api_url, params=data)

    def _clean_text(self, text):
        new_text = text
        for rgx_match in [r'\[.+\]']:
            new_text = re.sub(rgx_match, '', new_text)
        return new_text.strip()
    
    def _format_title(self, vol, chp):
        fin = []
        if vol != '':
            fin.append('Vol. ' + vol)
        if chp != '':
            fin.append('Ch. ' + chp)
        return ' '.join(fin)

    def top(self, count=5):
        soup = BeautifulSoup(self.requests.get(self.root_url, headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 Edg/80.0.361.69'}).text, features='html.parser')
        mgd = []
        mg_futures = {self._manga(x['href'].split('/')[2]):x['href'].split('/')[2] for x in soup.find('div', {'id': 'top_follows'}).find_all('a', {'class': 'manga_title'}, limit=count)}
        for future in mg_futures:
            try:
                data = munchify(future.result().json())
                time = dt.datetime.now()-dt.datetime.fromtimestamp(data.chapter[max({y: int(data.chapter[y].timestamp) for y in data.chapter}.items(), key = operator.itemgetter(1))[0]].timestamp)
                mgd.append({
                    'id': mg_futures[future],
                    'name': html.unescape(data.manga.title),
                    'cover': 'https://mangadex.org'+data.manga.cover_url,
                    'time': humanize.naturaltime(time)
                })
            except Exception as e:
                print(type(e), e, mg_futures[future])
                pass
        return mgd

    def updates(self, count=5):
        soup = BeautifulSoup(self.requests.get(self.update_url, headers={'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 Edg/80.0.361.69'}).text, features='html.parser')
        mgd = []
        mg_futures = {self._manga(x['href'].split('/')[2]):x['href'].split('/')[2] for x in soup.find_all('a', {'class': 'manga_title'}, limit=count)}
        for future in mg_futures:
            try:
                data = munchify(future.result().json())
                time = dt.datetime.now()-dt.datetime.fromtimestamp(data.chapter[max({y: int(data.chapter[y].timestamp) for y in data.chapter}.items(), key = operator.itemgetter(1))[0]].timestamp)
                mgd.append({
                    'id': mg_futures[future],
                    'name': data.manga.title,
                    'cover': 'https://mangadex.org'+data.manga.cover_url,
                    'time': humanize.naturaltime(time)
                })
            except Exception as e:
                print(type(e), e, mg_futures[future])
                pass
        return mgd

    def manga(self, iden):
        try:
            mg = munchify(self._manga(iden).result().json())
            chs = [{
                    'id': y,
                    'title': self._format_title(mg.chapter[y].volume, mg.chapter[y].chapter)
                } for y in mg.chapter if mg.chapter[y].lang_code == 'gb']
            dat = {
                'description': self._clean_text(html.unescape(mg.manga.description)),
                'author': html.unescape(mg.manga.author),
                'chapters_number': len([y for y in mg.chapter if mg.chapter[y].lang_code == 'gb']),
                'genres': [self.genres[y] for y in mg.manga.genres],
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
            ch = self._chapter(iden)
            if ch.status == 'delayed':
                return {
                    'status': 'delayed'
                }
            else:
                return {
                    'status': 'ok',
                    'result': [ch.server+ch.hash+'/'+x for x in ch.page_array]
                }
        except Exception as e:
            print(type(e), e)
            return {
                'status': 'error'
            }
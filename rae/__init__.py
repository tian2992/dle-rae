#!/usr/bin/python3
# -*- coding: utf-8 -*-

import ctypes
import re
import sys

import bs4
import requests

name = 'rae'

s = requests.Session()


class Article(object):
    def __init__(self, word, additional_information, definitions, complex_forms, links, verb_id):
        self.word = word
        self.additional_information = additional_information
        self.definitions = definitions
        self.complex_forms = complex_forms
        self.links = links
        self.verb_id = verb_id
        self.conjugations = []


class _Shared(object):
    PARSER = 'lxml'

    def __init__(self):
        pass

    @staticmethod
    def solve_challenge(c, slt, s1, s2, n, table):
        m = pow(ord(s2) - ord(s1) + 1, n)
        arr = [s1] * n
        chlg = None

        for _ in range(m-1):
            for i in range(n-1, -1, -1):
                arr[i] = chr(ord(arr[i]) + 1)

                if arr[i] <= s2:
                    break

                arr[i] = s1

            chlg = ''.join(arr)
            crc = -1

            for k in chlg + slt:
                index = ((crc ^ ord(k)) & 0x000000FF) * 9
                x = int(table[index:index+8], 16)
                crc = ctypes.c_int32(crc >> 8).value ^ ctypes.c_int32(x).value

            crc = abs(crc ^ -1)

            if crc == c:
                break

        return chlg

    @staticmethod
    def get_payload(r, rf):
        first = re.search('document\.forms\[0\]\.elements\[1\]\.value=\"(.+?):', r).group(1)
        slt = re.search('var slt = \"(.+?)\"', r).group(1)
        c = int(re.search('var c = (.+?)\r', r).group(1))
        s1 = re.search('var s1 = \'(.+?)\'', r).group(1)
        s2 = re.search('var s2 = \'(.+?)\'', r).group(1)
        n = int(re.search('var n = (.+?)\n', r).group(1))
        table = re.search('var table = \"(.+?)\"', r).group(1)

        chlg = _Shared.solve_challenge(c, slt, s1, s2, n, table)

        if not chlg:
            return None

        cr = ':'.join([first, chlg, slt, str(c)])

        return [['TS017111a7_id', '3'],
                ['TS017111a7_cr', cr],
                ['TS017111a7_76', '0'],
                ['TS017111a7_86', '0'],
                ['TS017111a7_md', '1'],
                ['TS017111a7_rf', rf],
                ['TS017111a7_ct', '0'],
                ['TS017111a7_pd', '0']]

    @staticmethod
    def do_request(request_url, rf, do_post=True):
        r = s.get(request_url)

        if r.status_code != requests.codes.ok:
            return None

        if do_post:
            payload = _Shared.get_payload(r.text, rf)

            if not payload:
                return None

            r = s.post(request_url, data=payload)

        return r if r.status_code == requests.codes.ok else None


class DLE(object):
    URL_DLE = 'http://dle.rae.es'
    URL_RANDOM_WORD = URL_DLE + '/srv/random'
    URL_TODAYS_WORD = URL_DLE + '/srv/wotd'
    URL_FETCH = URL_DLE + '/srv/fetch'
    URL_SEARCH = URL_DLE + '/srv/search'
    URL_AUTOCOMPLETE = URL_DLE + '/srv/keys'
    URL_RAE = 'http://www.rae.es/'
    MAX_LEMMAS_PAGE = 200
    M_EXACT = '&m=30'
    M_STARTS_WITH = '&m=31'
    M_ENDS_WITH = '&m=32'
    M_CONTAINS = '&m=33'

    def __init__(self):
        pass

    @staticmethod
    def _conjugate(name, data, col):
        result = [name]

        for i in data:
            result.append([i[0], i[col]])

        return result

    @staticmethod
    def conjugate_verb(verb):
        verb_id = DLE.search_word(verb)[0]

        return DLE.conjugate_id(verb_id)

    @staticmethod
    def conjugate_id(verb_id):
        r = _Shared.do_request(DLE.URL_FETCH + '?id=' + verb_id, DLE.URL_RAE)

        if r.status_code != requests.codes.ok:
            return None

        soup = bs4.BeautifulSoup(r.text, _Shared.PARSER)
        cnj = soup.find('table', class_='cnj')

        if not cnj:
            return None

        data = []
        h = []

        for row in cnj.find_all('tr'):
            cells = [cell.text.strip() for cell in row.find_all('td')]
            data.append(list(filter(None, cells)))
            heads = [header.text.strip() for header in row.find_all('th')]
            h.append(list(filter(None, heads)))

        data = list(filter(None, data))

        vc = [h[0][0]]
        vc.append([h[1][0], data[0][0]])
        vc.append([h[1][1], data[0][1]])
        vc.append([h[3][0], data[1][0]])
        vc.append(DLE._conjugate(h[5][0] + ' ' + h[6][3], data[2:10], 1))
        vc.append(DLE._conjugate(h[5][0] + ' ' + h[6][4], data[2:10], 2))
        vc.append(DLE._conjugate(h[5][0] + ' ' + h[15][0], data[10:18], 1))
        vc.append(DLE._conjugate(h[5][0] + ' ' + h[15][1], data[10:18], 2))
        vc.append(DLE._conjugate(h[5][0] + ' ' + h[24][0], data[18:26], 1))
        vc.append(DLE._conjugate(h[33][0] + ' ' + h[34][3], data[26:34], 1))
        vc.append(DLE._conjugate(h[33][0] + ' ' + h[34][4], data[26:34], 2))
        vc.append(DLE._conjugate(h[33][0] + ' ' + h[43][0], data[34:42], 1))
        vc.append(h[52][0])
        vc.append([data[42][0], data[42][1]])
        vc.append([data[43][0], data[43][1]])
        vc.append([data[44][0], data[44][1]])
        vc.append([data[45][0], data[45][1]])

        return vc

    @staticmethod
    def random_word():
        s.cookies.clear()

        r = _Shared.do_request(DLE.URL_RANDOM_WORD, DLE.URL_RANDOM_WORD, False)

        if not r:
            return None

        soup = bs4.BeautifulSoup(r.text, _Shared.PARSER)

        result = [article.text for article in soup.find_all('article')]

        return result if result else None

    @staticmethod
    def _request_word(word, after_host, m=None):
        url = DLE.URL_DLE + '/?w=' + word
        url2 = DLE.URL_DLE + after_host + word

        if m:
            url += m
            url2 += m

        if not _Shared.do_request(url, DLE.URL_RAE):
            return None

        r = _Shared.do_request(url2, url2)

        if not r:
            return None

        return bs4.BeautifulSoup(r.text, _Shared.PARSER)

    @staticmethod
    def _options(soup):
        results = []

        for op in soup.find('div', id='l0').find_all('a'):
            words = op.text.split('; ')
            word_ids = op.get('href').replace('fetch?id=', '').split('|')

            for word, word_id in zip(words, word_ids):
                results.append([word, word_id])

        return results

    @staticmethod
    def search_id(word_id):
        payload = {'id': word_id}
        r = s.get(DLE.URL_FETCH, data=payload)

        if r.status_code != requests.codes.ok:
            return None

        soup = bs4.BeautifulSoup(r.text, _Shared.PARSER)

        result = [article.text for article in soup.find_all('article')]

        return result if result else None

    @staticmethod
    def search_word(word, m=None):
        s.cookies.clear()

        soup = DLE._request_word(word, '/srv/search?w=', m)

        if not soup:
            return None

        f0 = soup.find('div', id='f0')

        verb_id = None

        if f0:
            result = f0.span.text
        else:
            result = []

            for article in soup.find_all('article'):
                a = article.text if article else DLE._options(soup)

                if not a:
                    return None

                result.append(a)

                e2 = soup.find('a', class_='e2')

                if e2:
                    verb_id = e2['href'].replace('fetch?id=', '')

        return result if isinstance(result, list) else [result, verb_id]

    @staticmethod
    def exact(word):
        return DLE.search_word(word, DLE.M_EXACT)

    @staticmethod
    def starts_with(prefix):
        return DLE.search_word(prefix, DLE.M_STARTS_WITH)

    @staticmethod
    def ends_with(suffix):
        return DLE.search_word(suffix, DLE.M_ENDS_WITH)

    @staticmethod
    def contains(substring):
        return DLE.search_word(substring, DLE.M_CONTAINS)

    @staticmethod
    def anagrams(word):
        s.cookies.clear()

        soup = DLE._request_word(word, '/srv/anagram?w=')

        return DLE._options(soup) if soup else None

    @staticmethod
    def todays_word():
        s.cookies.clear()

        if not _Shared.do_request(DLE.URL_DLE + '/?w=', DLE.URL_RAE):
            return None

        payload = {'': 'diccionario'}
        r = s.get(DLE.URL_SEARCH, data=payload)

        if r.status_code != requests.codes.ok:
            return None

        r = s.get(DLE.URL_TODAYS_WORD)

        if r.status_code != requests.codes.ok:
            return None

        soup = bs4.BeautifulSoup(r.text, _Shared.PARSER)
        word = soup.a
        word_id = word['href'].replace('id=', '')

        return [word.text, word_id]

    @staticmethod
    def get_lemmas():
        letters = 'aAáÁbBcCdDeEéÉfFgGhHiIíÍjJkKlLmMnNñÑoOóÓpPqQrRsStTuUúÚüÜvVwWxXyYzZ'

        prefix = letters[0]
        lemmas = []

        while prefix:
            tmp = None

            while not tmp:
                tmp = DLE.starts_with(prefix)

            current = [i[0] for i in tmp if i]

            nxt = True

            if len(current) < DLE.MAX_LEMMAS_PAGE:
                lemmas.extend(list(set(current) - set(lemmas)))
            else:
                prefix += letters[0]
                nxt = False

            if nxt:
                while prefix and prefix[-1] == letters[-1]:
                    prefix = prefix[:-1]

                if prefix:
                    i = letters.find(prefix[-1])
                    prefix = prefix[:-1] + letters[i + 1]

        lemmas.sort()

        return lemmas

    @staticmethod
    def autocomplete(substr):
        payload = {'callback': '', 'q': substr}
        r = s.get(DLE.URL_AUTOCOMPLETE, params=payload)

        if r.status_code != requests.codes.ok:
            return None

        return r.text.strip().replace('([', '').replace('])', '').replace('"', '').split(',')


class DPD(object):
    URL_SEARCH = 'http://lema.rae.es/dpd/?key='

    def __init__(self):
        pass

    @staticmethod
    def search(word):
        s.cookies.clear()

        if sys.version_info[0] == 2:
            import urllib
            w = urllib.quote_plus(word)
        elif sys.version_info[0] == 3:
            import urllib.parse
            w = urllib.parse.quote_plus(word)

        r = _Shared.do_request(DPD.URL_SEARCH + w, DPD.URL_SEARCH + w)

        if not r:
            return None

        soup = bs4.BeautifulSoup(r.text, _Shared.PARSER)
        article = soup.article

        return article.text if article else None


class DEJ(object):
    def __init__(self):
        pass


class DA(object):
    def __init__(self):
        pass


def main():
    pass


if __name__ == '__main__':
    main()

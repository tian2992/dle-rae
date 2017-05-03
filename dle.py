#!/usr/bin/python3

import bs4
import ctypes
import requests
import sys

host = 'http://dle.rae.es'
referer = 'http://www.rae.es/'
parser = 'lxml'

s = requests.Session()


def getChlg(c, slt, s1, s2, n, table):
    m = pow(ord(s2) - ord(s1) + 1, n)

    arr = [s1] * n

    for i in range(m-1):
        for j in range(n-1, -1, -1):
            arr[j] = chr(ord(arr[j]) + 1)

            if arr[j] <= s2:
                break
            else:
                arr[j] = s1

        chlg = ''.join(arr)
        stri = chlg + slt
        crc = ctypes.c_int32(0).value ^ ctypes.c_int32(-1).value

        for k in range(len(stri)):
            index = ((ctypes.c_int32(crc).value ^
                      ctypes.c_int32(ord(stri[k])).value) & 0x000000FF) * 9
            x = int(table[index:index+8], 16)
            crc = ctypes.c_int32(crc >> 8).value ^ ctypes.c_int32(x).value

        crc = abs(ctypes.c_int32(crc).value ^ ctypes.c_int32(-1).value)

        if crc == c:
            break

    return chlg


def doRequest(requestUrl, rf):
    response = s.get(requestUrl).text

    tmp = response.index('document.forms[0].elements[1].value=\"') + 37
    first = response[tmp:response.index(':', tmp)]

    tmp = response.index('var slt = \"') + 11
    slt = response[tmp:response.index('\"', tmp)]

    tmp = response.index('var c = ') + 8
    c = int(response[tmp:response.index('\r', tmp)])

    tmp = response.index('var s1 = \'') + 10
    s1 = response[tmp:response.index('\'', tmp)]

    tmp = response.index('var s2 = \'') + 10
    s2 = response[tmp:response.index('\'', tmp)]

    tmp = response.index('var n = ') + 8
    n = int(response[tmp:response.index('\n', tmp)])

    tmp = response.index('var table = \"') + 13
    table = response[tmp:response.index('\"', tmp)]

    chlg = getChlg(c, slt, s1, s2, n, table)

    cr = first + ':' + chlg + ':' + slt + ':' + str(c)

    payload = (('TS017111a7_id', '3'),
               ('TS017111a7_cr', cr),
               ('TS017111a7_76', '0'),
               ('TS017111a7_86', '0'),
               ('TS017111a7_md', '1'),
               ('TS017111a7_rf', rf),
               ('TS017111a7_ct', '0'),
               ('TS017111a7_pd', '0'))

    s.headers.update({'Referer': requestUrl})
    s.headers.update({'Accept-Encoding': 'gzip, deflate'})
    s.headers.update({'Cache-Control': 'max-age=0'})
    s.headers.update({'Origin': host})

    return s.post(requestUrl, data=payload)


def search(word):
    s.headers.update({'Upgrade-Insecure-Requests': '1'})
    s.headers.update({'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'})
    s.headers.update({'Referer': referer})
    s.headers.update({'Accept-Language': 'es-ES,es;q=0.8'})
    s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'})
    s.headers.update({'Accept-Encoding': 'gzip, deflate, sdch'})

    s.cookies = requests.utils.cookiejar_from_dict({'cookies_rae': 'aceptada'})

    url1 = host + '/?w=' + word
    url2 = host + '/srv/search?w=' + word

    doRequest(url1, referer)          # get the cookie
    response = doRequest(url2, url2)  # get the definition

    soup = bs4.BeautifulSoup(response.text, parser)

    return soup.find('article').get_text()


if __name__ == '__main__':
    print(search(sys.argv[1]))

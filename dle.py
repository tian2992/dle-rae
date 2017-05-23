#!/usr/bin/python3

import bs4
import ctypes
import requests
import time

host = 'http://dle.rae.es'
referer = 'http://www.rae.es/'
parser = 'lxml'

s = requests.Session()


def solveChallenge(c, slt, s1, s2, n, table):
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

    ## Should add a try-catch here, Response might not include the substring value.
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

    chlg = solveChallenge(c, slt, s1, s2, n, table)

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


def conjugate(name, data, col):
    result = name + '\n'

    for i in range(0, 8):
        result += data[i][0] + ' ' + data[i][col] + '\n'

    return result


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

    f0 = soup.find('div', id='f0')

    if f0:  # this exists if the word was not found
        result = f0.find('span').text
    else:
        article = soup.find('article')

        if article:
            result = article.get_text()
        else:
            options = soup.findAll('a')
            links = []
            i = 1

            for op in options:
                links.append(op.get('href'))
                print(str(i) + '. ' + op.text)
                i += 1

            ## This should not depend on user interaction.
            opt = int(input('\nSeleccione una opcion: ')) - 1

            url3 = host + '/srv/' + links[opt]

            response = s.get(url3)
            soup = bs4.BeautifulSoup(response.text, parser)
            result = soup.find('article').get_text()

        e2 = soup.find('a', class_='e2')

        if e2:
            url4 = host + '/srv/' + e2['href']

            time.sleep(3)

            response = s.get(url4)
            soup = bs4.BeautifulSoup(response.text, parser)

            rows = soup.find('table', class_='cnj').find_all('tr')

            data = []
            headers = []

            for row in rows:
                cells = [cell.text.strip() for cell in row.find_all('td')]
                data.append([cell for cell in cells if cell])
                heads = [header.text.strip() for header in row.find_all('th')]
                headers.append([header for header in heads if header])

            data = [e for e in data if e]

            conjugation = headers[0][0] + '\n'
            conjugation += headers[1][0] + ': ' + data[0][0] + '\n'
            conjugation += headers[1][1] + ': ' + data[0][1] + '\n'
            conjugation += headers[3][0] + ': ' + data[1][0] + '\n'
            conjugation += '\n'
            conjugation += conjugate(headers[5][0] + ' ' + headers[6][3], data[2:10], 1) + '\n'
            conjugation += conjugate(headers[5][0] + ' ' + headers[6][4], data[2:10], 2) + '\n'
            conjugation += conjugate(headers[5][0] + ' ' + headers[15][0], data[10:18], 1) + '\n'
            conjugation += conjugate(headers[5][0] + ' ' + headers[15][1], data[10:18], 2) + '\n'
            conjugation += conjugate(headers[5][0] + ' ' + headers[24][0], data[18:26], 1) + '\n'
            conjugation += conjugate(headers[33][0] + ' ' + headers[34][3], data[26: 34], 1) + '\n'
            conjugation += conjugate(headers[33][0] + ' ' + headers[34][4], data[26: 34], 2) + '\n'
            conjugation += conjugate(headers[33][0] + ' ' + headers[43][0], data[34:42], 1) + '\n'
            conjugation += headers[52][0] + '\n'
            conjugation += data[42][0] + ' ' + data[42][1] + '\n'
            conjugation += data[43][0] + ' ' + data[43][1] + '\n'
            conjugation += data[44][0] + ' ' + data[44][1] + '\n'
            conjugation += data[45][0] + ' ' + data[45][1]

            result += '\n' + conjugation + '\n'

    return result

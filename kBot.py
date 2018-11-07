import requests
import time
import threading
import argparse
import pprint
import os

from requests_html import HTMLSession
from bs4 import BeautifulSoup


def get_keys_send_kudos(session, proxy, counter):
    session.proxies = {
        'http': proxy,
        'https': proxy
    }

    accept_adult = {
        'view_adult': 'true'
    }

    try:
        with session.get(url=args.work, params=accept_adult, timeout=10) as response:
            soup = BeautifulSoup(response.content, features="html.parser")

            form = soup.find('form',
                             {
                                 'id': 'new_kudo'
                             })

            if not form:
                return

            hidden_tags = form.find_all('input', type='hidden')

            if not hidden_tags:
                return

            inputs = []
            for tags in hidden_tags:
                inputs.append(tags.get('value'))

            keys = {
                'authenticity_token': inputs[1],
                'kudo[commentable_id]': inputs[2],
                'kudo[commentable_type]': inputs[3],
                'utf8': inputs[0]
            }

            sc = send_k(session, keys)

            if sc == 201:
                counter.add(1)
            elif sc == 422:
                pass

    except requests.exceptions.HTTPError as e:
        print("Status code {}".format(e))
    except requests.exceptions.ConnectionError:
        pass
        # print("Cannot connect to proxy")


def send_k(session, keys):
    with session.post(url='https://archiveofourown.org/kudos.js', data=keys,
                      verify=True, timeout=10) as response:
        return response.status_code


def gift(proxy, counter):
    with HTMLSession() as session:
        get_keys_send_kudos(session, proxy, counter)


class COUNT:
    def __init__(self, x):
        self.x = x

    def get(self):
        return self.x

    def set(self, x):
        self.x = x

    def add(self, i):
        self.x += i


def display(counter, stop):
    while True:
        if stop.x:
            break
        os.system('cls' if os.name == 'nt' else 'clear')
        pprint.pprint("Start kudoBot version 1.1")
        pprint.pprint("{} gifted kudos".format(counter.x))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=str, help='url of work on ao3')
    parser.add_argument('--proxy_list', type=str, help='text document of listed proxies')

    args = parser.parse_args()

    with open(args.proxy_list) as f:
        proxies = f.readlines()

    proxies = [x.rstrip('\n') for x in proxies]

    success = COUNT(0)
    stop = COUNT(False)
    threads = []

    for p in proxies:
        thread = threading.Thread(target=gift, args=(p, success))
        threads.append(thread)

    display_thread = threading.Thread(target=display, args=(success, stop))
    display_thread.setDaemon(True)
    display_thread.start()

    ts = time.time()
    for t in threads:
        t.start()

    for t in threads:
        t.join()

    te = time.time()

    stop.set(True)
    pprint.pprint("{} seconds".format(te - ts))



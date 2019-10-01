class Sleeper:
    def __init__(self, block_secs=60 * 20):
        self.url = ''
        self.block_times = 1
        self.block_secs = block_secs

    def sleep(self, url):
        import time

        if self.url == url:
            self.block_times += 1
        else:
            self.url = url
            self.block_times = 1
        time.sleep(self.block_secs * self.block_times)
        self.block_secs *= 1.3


class ProxyPool:
    def __init__(self):
        from itertools import cycle
        from time import time

        self.proxies = self.get_proxies()
        self.proxy_pool = cycle(self.proxies)
        self.bad_proxy_cnt = {}
        self.bad_proxy_cnt_limit = 5
        self.start_time = time()
        self.time_limit = 60 * 30

    def __next__(self):
        from time import time

        if (time() - self.start_time > self.time_limit) or len(
                self.proxies) < 5:
            self.__init__()
        return next(self.proxy_pool)

    def __len__(self):
        return len(self.proxies)

    def add_bad_proxy(self, proxy):
        from itertools import cycle

        if proxy not in self.bad_proxy_cnt:
            self.bad_proxy_cnt[proxy] = 1
        else:
            self.bad_proxy_cnt[proxy] += 1
            if self.bad_proxy_cnt[proxy] > self.bad_proxy_cnt_limit:
                self.proxies -= {proxy}
                self.proxy_pool = cycle(self.proxies)

    @staticmethod
    def get_proxies():
        import requests
        from lxml.html import fromstring
        from tqdm import tqdm

        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = []
        valid_proxies = set()
        for i in parser.xpath('//tbody/tr'):
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                # Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                                  i.xpath('.//td[2]/text()')[0]])
                proxies.append(proxy)

        for proxy in tqdm(proxies):
            try:
                r = requests.get(url, proxies={"http": proxy, "https": proxy})
                valid_proxies |= {proxy}
                if len(valid_proxies) > 10:
                    break
            except Exception:
                pass
        return valid_proxies


def check_env():
    try:
        import requests
        import efficiency
        import tqdm
        import lxml
    except:
        import os
        os.system('pip install efficiency requests tqdm lxml')


def get_html(url, hour_max=800, use_proxy=False):
    import time
    import requests
    from efficiency.log import show_time

    time.sleep(60 * 60 / hour_max)

    if use_proxy:
        proxy = next(proxy_pool)

        try:
            r = requests.get(url, proxies={"http": proxy, "https": proxy})
        except Exception:
            proxy_pool.add_bad_proxy(proxy)
            get_html(url)
            return
    else:
        try:
            r = requests.get(url)
        except:
            show_time('[Warn] {} is blocked'.format(url))
            save_json()

            sleeper.sleep(url)
            r = requests.get(url)

    if r.status_code == 403:
        show_time('[Warn] {} is blocked'.format(url))
        save_json()

        sleeper.sleep(url)
        get_html(url)
    else:
        if r.status_code == 200:
            return r.text


def get_content(bit_id='OpjqIE', hour_max=800):
    import json

    url = 'https://bitly.com/{}+'.format(bit_id)
    html = get_html(url, hour_max=hour_max)
    if html:
        try:
            parts = html.split('window.InfoPlus.start(\n', 1)[1]
            parts = parts.split(',\n', 2)[:2]
            parts = [json.loads(part) for part in parts]
            for k, v in parts[1].items():
                if k in parts[0]:
                    if v != parts[0][k]:
                        import pdb
                        pdb.set_trace()
            parts[0].update(parts[1])
            return parts[0]
        except:
            import pdb
            pdb.set_trace()


def make_permutations(length, shard_id, hour_max, shard_size=20000):
    from string import digits, ascii_uppercase, ascii_lowercase
    import itertools
    from tqdm import tqdm

    chars = digits + ascii_uppercase + ascii_lowercase

    if length > 0:
        permutations = list(itertools.product(chars, repeat=length))
        permutations = [i for i in permutations if i not in set(data.keys())]
    else:
        permutations = list(itertools.product(chars, repeat=1))[:1]
    total_len = len(permutations)
    print('[Info] Total length of this permutations:', total_len)
    print('[Info] Will be saved to:', save_to)
    permutations = permutations[
                   shard_size * shard_id:shard_size * (shard_id + 1)]
    tbar = tqdm(permutations)
    tbar.set_description('{}, {}, {}/hr'.format(save_to, total_len, hour_max))
    return tbar


def save_json():
    import json
    from efficiency.log import fwrite
    fwrite(json.dumps(data, indent=4), save_to)


def get_init_data():
    import os
    import json
    from efficiency.log import fwrite

    data = {}
    if os.path.isfile(save_to):
        with open(save_to) as f: content = f.read(); data = json.loads(content)
        fwrite(content, save_to + '.prev')
        print(
            '[Info] Previous data file exists. Made a backup at ' + save_to + '.prev')
    return data


def main(length, shard_id, hour_max, shard_size=20000, save_size=2000):
    tbar = make_permutations(length, shard_id, hour_max, shard_size=shard_size)

    for item in tbar:
        bit_id = ''.join(item)
        content = get_content(bit_id, hour_max=hour_max)
        if content is not None:
            data[bit_id] = content
            if len(data) % save_size == 0:
                save_json()
    save_json()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('Args for Web Crawler')
    parser.add_argument('-len', default=1, type=int,
                        help='the length of bit id in the urls to crawl')
    parser.add_argument('-shard', default=0, type=int,
                        help='the length of bit id in the urls to crawl')
    parser.add_argument('-hour_max', default=800, type=int,
                        help='number of downloads permited per hour')
    parser.add_argument('-use_proxy', action='store_true',
                        help='whether to use proxy when scraping')
    args = parser.parse_args()

    check_env()

    if args.use_proxy:
        import signal


        def handler(signum, frame):
            raise Exception("end of time")


        signal.signal(signal.SIGALRM, handler)
        signal.alarm(1)

        proxy_pool = ProxyPool()
        args.hour_max *= len(proxy_pool)

    sleeper = Sleeper()

    save_to = 'bitly_{}_{}.json'.format(args.len, args.shard)
    data = get_init_data()

    main(args.len, args.shard, args.hour_max)

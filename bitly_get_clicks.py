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
        self.block_secs *= 1.5


class ProxyPool:
    def __init__(self, proxy_file=''):
        from itertools import cycle
        from time import time

        proxies = self.get_proxies(proxy_file)
        self.proxies = self.verify_proxies(proxies)
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
    def get_proxies(proxy_file=''):
        if proxy_file:
            with open(proxy_file) as f:
                proxies = [line.strip() for line in f if line.strip()]
            return proxies

        import requests
        from lxml.html import fromstring

        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = []
        for i in parser.xpath('//tbody/tr'):
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                # Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                                  i.xpath('.//td[2]/text()')[0]])
                proxies.append(proxy)
        return proxies

    @staticmethod
    def verify_proxies(proxies):
        import requests
        from tqdm import tqdm

        print('[Info] Checking proxies:', proxies)

        url = 'https://free-proxy-list.net/'
        valid_proxies = set()
        for proxy in tqdm(proxies):
            try:
                r = requests.get(url, proxies={"http": proxy, "https": proxy})
                valid_proxies |= {proxy}
                if len(valid_proxies) > 10:
                    break
            except Exception:
                pass
        if not valid_proxies:
            print('[Info] No valid proxies. Exiting program...')
            import sys
            sys.exit()

        print('[Info] Using proxies:', valid_proxies)

        return valid_proxies


def check_env():
    try:
        import requests
        import efficiency
        import tqdm
        import lxml
    except ImportError:
        import os
        os.system('pip install efficiency requests tqdm lxml')
        os.system('pip3 install efficiency requests tqdm lxml')


def get_html(url, use_proxy=False):
    import time
    import requests
    from efficiency.log import show_time

    time.sleep(interval)
    headers = {'User-Agent': next(user_agents)}

    if use_proxy:
        proxy = next(proxy_pool)

        try:
            r = requests.get(url, proxies={"http": proxy, "https": proxy},
                             headers=headers)
        except Exception:
            proxy_pool.add_bad_proxy(proxy)
            get_html(url)
            return
    else:
        try:
            r = requests.get(url, headers=headers)
        except:
            show_time(
                '[Warn] {} is blocked for {}s'.format(url, sleeper.block_secs))
            save_json()

            sleeper.sleep(url)
            r = requests.get(url, headers=headers)

    if r.status_code == 403:
        show_time(
            '[Warn] {} is blocked for {}s'.format(url, sleeper.block_secs))
        save_json()

        sleeper.sleep(url)
        get_html(url)
    else:
        if r.status_code == 200:
            return r.text


def get_content(bit_id='2pa6pME'):
    import json

    url = 'https://bitly.com/{}+'.format(bit_id)
    html = get_html(url)
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
            dic = parts[0]
            keys = ['title', 'long_url', 'global_clicks', 'user_clicks',
                    'global_created_at', 'created_at',
                    'hash', 'global_hash', 'user_hash', 'enterprise_user',
                    'confidential_metrics_visible', 'confidential_metrics', ]
            dic = {k: dic[k] for k in keys}
            return dic
        except:
            import pdb
            pdb.set_trace()


def get_permutations(shard_id, length=7, shard_size=None):
    from string import digits, ascii_uppercase, ascii_lowercase
    from tqdm import tqdm

    chars = digits + ascii_uppercase + ascii_lowercase
    uid_file = './data/bitid_{:03d}.txt'.format(shard_id)

    with open(uid_file) as f:
        uids = f.read().strip()
        uids = uids.split()[:shard_size]
        uids = [uid[:length] for uid in uids]

    total_len = len(uids)
    print('[Info] Total length of this permutations:', total_len)
    print('[Info] Will be saved to:', save_to)

    uids = list(set(uids) - set(data.keys()))

    tbar = tqdm(uids)
    tbar.set_description(
        '{}, {}, {}sec'.format(save_to, total_len, interval))
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


def main(shard_id, length=7, save_size=2000, shard_size=20000):
    tbar = get_permutations(shard_id, length=length, shard_size=shard_size)

    for bit_id in tbar:
        content = get_content(bit_id)
        data[bit_id] = content
        if len(data) % save_size == 0:
            save_json()
    save_json()


if __name__ == '__main__':
    import argparse
    from itertools import cycle

    parser = argparse.ArgumentParser('Args for Web Crawler')
    parser.add_argument('-len', default=7, type=int,
                        help='the length of bit id in the urls to crawl')
    parser.add_argument('-shard', default=0, type=int,
                        help='the length of bit id in the urls to crawl')
    parser.add_argument('-shard_size', default=None, type=int,
                        help='number of urls to crawl')
    parser.add_argument('-hour_max', default=800, type=int,
                        help='number of downloads permited per hour')
    parser.add_argument('-use_proxy', action='store_true',
                        help='whether to use proxy when scraping')
    parser.add_argument('-proxy_file', default='', type=str,
                        help='what file to look up the proxy addresses')
    args = parser.parse_args()

    check_env()

    if args.use_proxy:
        import signal


        def handler(signum, frame): raise Exception("end of time")


        signal.signal(signal.SIGALRM, handler)

        proxy_pool = ProxyPool(args.proxy_file)
        args.hour_max *= len(proxy_pool)

    sleeper = Sleeper()

    interval = int(60 * 60 / args.hour_max)
    save_to = 'ctr_{:03d}.json'.format(args.shard)
    data = get_init_data()
    user_agents = cycle([
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    ])

    main(args.shard, length=args.len, shard_size=args.shard_size)

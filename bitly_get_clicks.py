def check_env():
    try:
        import requests
        import efficiency
        import tqdm
    except:
        import os
        os.system('pip install efficiency requests tqdm')


def get_html(url):
    import requests
    import time

    r = requests.get(url)
    status_code = r.status_code
    if status_code == 403:
        print('[Warn] {} is blocked'.format(url))
        save_json()

        time.sleep(60 * 10)
        get_html(url)
    elif status_code == 404:
        return None
    elif status_code == 200:
        return r.text


def get_content(bit_id='OpjqIE', hour_max=350):
    import json
    import time

    url = 'https://bitly.com/{}+'.format(bit_id)
    html = get_html(url)
    time.sleep(60 * 60 / hour_max)
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


def make_permutations(length, shard_id, shard_size=20000):
    from string import digits, ascii_uppercase, ascii_lowercase
    import itertools
    from tqdm import tqdm

    chars = digits + ascii_uppercase + ascii_lowercase

    if length > 0:
        permutations = list(itertools.product(chars, repeat=length))
    else:
        permutations = list(itertools.product(chars, repeat=1))[:1]
    print('[Info] Total length of this permutations:', len(permutations))
    print('[Info] Will be saved to:', save_to)
    permutations = permutations[
                   shard_size * shard_id:shard_size * (shard_id + 1)]
    tbar = tqdm(permutations)
    tbar.set_description('{}, {}'.format(save_to, len(permutations)))
    return tbar


def save_json():
    import json
    from efficiency.log import fwrite
    fwrite(json.dumps(data, indent=4), save_to)


def main(length, shard_id, shard_size=20000, save_size=2000):
    tbar = make_permutations(length, shard_id, shard_size=shard_size)

    for item in tbar:
        bit_id = ''.join(item)
        content = get_content(bit_id)
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
    args = parser.parse_args()

    check_env()

    data = {}
    save_to = 'bitly_{}_{}.json'.format(args.len, args.shard)

    main(args.len, args.shard)

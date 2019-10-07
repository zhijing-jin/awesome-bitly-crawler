from os.path import isdir, dirname, realpath, basename
from os import listdir, path
from efficiency.function import shell
from efficiency.log import show_var


class FileManager():

    def __init__(self, dir=dirname(realpath(__file__)),
                 file_filter=lambda f: True):
        self.files = self.recurse_files(dir, file_filter=file_filter)

    @staticmethod
    def recurse_files(folder, file_filter=lambda f: True):
        if isdir(folder):
            return [path.join(folder, f) for f in listdir(folder)
                    if file_filter(f)]
        return [folder]

    def rename_files(self, prefix='My_mp3_'):
        for f in self.files:
            dir = dirname(f)
            fname = basename(f)
            new_fname = prefix + fname
            new_f = path.join(dir, new_fname)
            cmd = 'mv "{f}" "{new_f}"'.format(f=f, new_f=new_f)
            show_var(['cmd'])
            shell(cmd)


def get_most_common_in_list(ls, most_common_n=1):
    from collections import Counter
    cnt = Counter(ls)
    return cnt.most_common(most_common_n)


def check():
    import json

    file = '/home/ubuntu/proj/1908_clickbait/bitly/bitly.json'
    with open(file) as f:
        data = json.load(f)
    show_var(['len(data)', 'list(data.items())[99]'])
    titles = []
    for item in data.values():
        titles.append(item['title'])


    get_most_common_in_list(titles, most_common_n=10)

    bad_titles = {None, '金沙澳门官方网址_', 'Featured Content on Myspace',
                  'Google Maps', 'Games | SYFY WIRE', 'Trending on Offbeat',
                  'Page Not Found', 'YouTube',
                  'QuickSnapper.com domain is for sale | Buy with Epik.com',
                  'Twitter / Account Suspended',
                  'Jason, 443 AI (@JasonInAI) | Twitter',
                  'interactive investor: low cost online trading & investment platform',
                  'Yahoo',
                  'TechRapidly- Blog Provide Tech and Business Tips & Solutions',
                  'Tech & Startup Events In New York - GarysGuide (#1 Resource for NYC Tech)',
                  'The Marmoset Song | quietube', 'Login on Twitter',
                  'Prepare your taste buds...', 'Good night, Posterous',
                  'MSN | Outlook, Office, Skype, Bing, Breaking News, and Latest Videos',
                  'Venture Capitalists Need Money, Too – Gigaom',
                  '502 Bad Gateway', '2008Q4a Home Tour Survey',
                  'Are you human, bot or alien? | mobile9', 'Twitpic',
                  'When Robot Programmers get bored - YouTube',
                  'Account Suspended',
                  'Free Web Hosting - Your Website need to be migrated',
                  '404 Not Found - Web Partner',
                  'Resort | Free Parking | Trump Las Vegas, NV - Booking.com',
                  'TVShowsOnDVD.com - Goodbye',
                  'Get Satisfaction - Customer Communities For Social Support, Social Marketing & Customer Feedback',
                  'Google',
                  'Warning! | There might be a problem with the requested link',
                  'Designer Clothes, Shoes & Bags for Women | SSENSE',
                  'NRKbeta',
                  "Movie Review: Paul Farhi Reviews 'Yoo-Hoo, Mrs. Goldberg' - washingtonpost.com",
                  'ogmaciel.com is coming soon',
                  'Nico Lumma - Hamburg, Deutschland | about.me',
                  'Abattement Fiscal'}
    good_data = {k:v for k,v in data.items() if 'nytimes' in v['long_url']}
    # good_data = {k:v for k,v in data.items() if v['title'] not in bad_titles}
    show_var(['len(good_data)'])
    import pdb;
    pdb.set_trace()

def check_time():
    from datetime import datetime
    timestamp = 1521099579
    datetime.fromtimestamp(timestamp)
def main():
    import os
    import json
    from efficiency.log import fwrite

    data = {}
    dir = '/home/ubuntu/proj/1908_clickbait/bitly'
    file_filter = lambda f: f.startswith('bitly_') and f.endswith('.json')

    fm = FileManager(dir=dir, file_filter=file_filter)
    print(json.dumps(fm.files, indent=4))
    for file in fm.files:
        with open(file) as f: content = json.load(f)
        data.update(content)
        show_var(
            ["file", "len(content)", "len(data)", "list(content.keys())[:3]"])

    data = dict(sorted(data.items()))
    fwrite(json.dumps(data, indent=4), os.path.join(dir, 'bitly.json'))


if __name__ == '__main__':
    check()

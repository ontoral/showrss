import os
import feedparser
import re
import datetime, time
from sqlite3 import dbapi2 as sqlite3
import urllib

SHOWRSS_FEED = 'http://showrss.karmorra.info/rss.php?user_id=94858&hd=0&proper=1'
TORRENT_PATH = 'torrents/'

class Entry(object):
    filename_template = '{showname}.S{season:02d}E{episode:02d}.torrent'
    def __init__(self, entry):
        m = re.search('(.*) [sS]?([0-9]{1,2})[eExX]([0-9]{1,2}) .*', entry.title)
        self.id = entry.link.split('/')[-1].split('.')[0]
        self.date = int(time.mktime(entry.published_parsed))
        self.showname = m.group(1)
        self.season = int(m.group(2))
        self.episode = int(m.group(3))
        self.filename = self.filename_template.format(**self.__dict__).replace(' ', '.')
        self.url = entry.link

def main():
    d = feedparser.parse(os.environ.get('SHOWRSS_FEED', SHOWRSS_FEED))

    for ee in d.entries:
        entry = Entry(ee)
        filename = os.path.join(os.environ.get('TORRENT_PATH', TORRENT_PATH),
                                entry.filename)
        urllib.urlretrieve(entry.url, filename)

        msg = 'Downloaded torrent file: S{season:02d}E{episode:02d} - {showname}'
        print msg.format(**entry.__dict__)


if __name__ == '__main__':
    main()

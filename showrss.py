import feedparser
import re
import datetime, time
from sqlite3 import dbapi2 as sqlite3

FEED = 'http://showrss.karmorra.info/rss.php?user_id=94858&hd=0&proper=1'

def get_show_info(title):
    m = re.search('(.*) [sS]?([0-9]{1,2})[eEx]([0-9]{1,2}) .*', title)
    return dict(showname=m.group(1), season=int(m.group(2)), episode=int(m.group(3)))

def main():
    d = feedparser.parse(FEED)

    for entry in d.entries:
        info = get_show_info(entry.title)
        info['link'] = entry.link
        info['published'] = datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed))

        print info


if __name__ == '__main__':
    main()

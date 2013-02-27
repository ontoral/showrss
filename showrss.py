#!/usr/bin/env python

# Standard library imports
import argparse
import datetime
import os
import re
# from sqlite3 import dbapi2 as sqlite3
import subprocess
import time

# Other imports
import feedparser

SHOWRSS_FEED = 'http://showrss.karmorra.info/rss.php?user_id=94858&hd=0&proper=1&magnets=true'
TORRENT_PATH = '/home/pi/torrents/'
SHOWRSS_TIMESTAMP = '.timestamp'
PRODUCTION = False


class Entry(object):
    def __init__(self, entry):
#        print 'entry:', len(entry), entry.keys(), '\n', entry
        m = re.search('(.*) [sS]?([0-9]{1,2})([eExX]([0-9]{1,2}))* .*', entry.title)
        self.timestamp = int(time.mktime(entry.published_parsed))
        self.showname = m.group(1)
        self.season = int(m.group(2))
        self.episode = int(m.group(3)[-2:])
        m = re.search('.*\?xt=([^&]*).*', entry.link)
        self.hash = m.group(1)
        self.url = entry.link


def main(timestamp=0):
    d = feedparser.parse(os.environ.get('SHOWRSS_FEED', SHOWRSS_FEED))

    newstamp = timestamp
    for ee in d.entries:
        entry = Entry(ee)
        if entry.timestamp > timestamp:
            newstamp = max(newstamp, entry.timestamp)
            subprocess.call(['transmission-remote', '-a', entry.url])
            msg = 'Added magnet: S{season:02d}E{episode:02d} - {showname}'
            print msg.format(**entry.__dict__)
        elif not PRODUCTION:
            msg = 'Skipping: S{season:02d}E{episode:02d} - {showname}'
            print msg.format(**entry.__dict__)

    print datetime.datetime.fromtimestamp(newstamp), '- done!'
    return newstamp


if __name__ == '__main__':
    filename = os.environ.get('SHOWRSS_TIMESTAMP', SHOWRSS_TIMESTAMP)
    if os.path.exists(filename):
        # Read timestamp for most recently posted feed item
        with file(filename, 'r') as settings:
            timestamp = int(settings.readline())
    else:
        timestamp = 0

    timestamp = main(timestamp)

    # Record the most recent feed timestamp in a file
    if PRODUCTION:
        with file(filename, 'w') as settings:
            settings.write(str(timestamp) + '\n')

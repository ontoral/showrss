#!/usr/bin/env python

# Standard library imports
import argparse
import datetime
import os
import re
# from sqlite3 import dbapi2 as sqlite3
import subprocess
import tempfile
import time

# Other imports
import feedparser


# Config
SHOWRSS_FEED = 'http://showrss.info/rss.php?user_id=94858&hd=0&proper=1'
SHOWRSS_FEED = os.environ.get('SHOWRSS_FEED', SHOWRSS_FEED)
SHOWRSS_TIMESTAMP = os.environ.get('SHOWRSS_TIMESTAMP', os.path.expanduser('~/.timestamp'))
SHOWRSS_DEBUG = bool(os.environ.get('SHOWRSS_DEBUG', False))


class Entry(object):
    def __init__(self, entry):
        #print 'entry:', len(entry), entry.keys(), '\n', entry
        #print entry.title
        regexp = '(.*)[ .-][sS]?([0-9]{1,2})[eExX]([0-9]{1,2})*.*'
        m = re.search(regexp, entry.title)
        self.timestamp = int(time.mktime(entry.published_parsed))
        self.showname = m.group(1)
        self.season = 0
        self.episode = 0
        try:
            self.season = int(m.group(2))
            self.episode = int(m.group(3))
        except:
            pass
        m = re.search('.*\?xt=([^&]*).*', entry.link)
        self.hash = m.group(1)
        self.url = entry.link

    def __repr__(self):
        return '<Magnet: {0.hash}, {0.showname} S{0.season:02d}E{0.episode:02d}>'.format(self)


def main(timestamp):
    d = feedparser.parse(SHOWRSS_FEED)

    newstamp = timestamp
    for ee in d.entries:
        entry = Entry(ee)
        #print entry
        if entry.timestamp > timestamp:
            newstamp = max(newstamp, entry.timestamp)
            subprocess.call(['transmission-remote', '-a', entry.url])
            msg = 'Added magnet: S{season:02d}E{episode:02d} - {showname}'
            print msg.format(**entry.__dict__)
        elif SHOWRSS_DEBUG:
            msg = 'Skipping: S{season:02d}E{episode:02d} - {showname}'
            print msg.format(**entry.__dict__)

    print datetime.datetime.fromtimestamp(newstamp), '- done!'
    return newstamp


if __name__ == '__main__':
    description = """Download TV torrents from showRSS feeds.

    Read a torrent RSS feed from http://showrss.karmorra.info, and add all
    new magnet links to a locally running instance of transmission, via
    transmission-remote."""
    parser = argparse.ArgumentParser(description=description)

    try:
        session_info = subprocess.check_output(['transmission-remote',
                                                '-si'])
        download_dir = re.search('Download directory: ([^\s]*)',
                                 session_info)
    except OSError, e:
        print 'Transmission daemon not found.'

    filename = SHOWRSS_TIMESTAMP
    if os.path.exists(filename):
        # Read timestamp for most recently posted feed item
        with file(filename, 'r') as settings:
            timestamp = int(settings.readline())
    else:
        timestamp = 0

    timestamp = main(timestamp)

    # Record the most recent feed timestamp in a file
    if not SHOWRSS_DEBUG:
        with file(filename, 'w') as settings:
            settings.write(str(timestamp) + '\n')


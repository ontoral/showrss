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
        self.title = m.group(1)
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
        return '<Magnet: {0.hash}, {0}>'.format(self)

    def __str__(self):
        return '{0.title} S{0.season:02d}E{0.episode:02d}'.format(self)


def main(args, timestamp, download_dir):
    d = feedparser.parse(SHOWRSS_FEED)

    print 'ShowRSS Feed Downloader'
    newstamp = timestamp
    for ee in d.entries:
        entry = Entry(ee)
        #print entry
        download = False

        # List feed items and take no action
        if args.list_only:
            status = '*' if entry.timestamp > timestamp else ''
            print '{}{}'.format(status, entry)
            continue

        # Prompt [y/N] each feed item before download
        if args.interactive:
            answer = raw_input('Download "{}"? [yNq] '.format(entry)).lower()
            if answer in ['quit', 'q']:
                break
            download = answer in ['yes', 'y']
        elif entry.timestamp > timestamp:
            download = True

        # Download or skip feed items accordingly
        if download:
            newstamp = max(newstamp, entry.timestamp)
            path = os.path.join(download_dir, 'video', 'tv', entry.title)
            #print 'Download to: {}'.format(path)
            result = subprocess.check_output(['transmission-remote',
                                              '-a', entry.url])
            print '    Adding   {}... {}'.format(entry, result.split()[-1])
        else:
            if args.verbose:
                print '    Skipping {}'.format(entry)

    print datetime.datetime.fromtimestamp(newstamp), '- done!'
    return newstamp


if __name__ == '__main__':
    description = """Download TV torrents from showRSS feeds.

    Read a torrent RSS feed from http://showrss.info, and add all
    new magnet links to a locally running instance of transmission, via
    transmission-remote."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='prompt for confirmation on all feed items.')
    parser.add_argument('-l', '--list', dest='list_only', action='store_true',
                        help='list available feed items (no action).')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='more output.')

    try:
        session_info = subprocess.check_output(['transmission-remote',
                                                '-si'])
        download_dir = re.search('Download directory: ([^\s]*)',
                                 session_info).group(1)
    except OSError, e:
        print 'Transmission daemon not found.'
        exit()

    timestamp = 0
    filename = SHOWRSS_TIMESTAMP
    if os.path.exists(filename):
        # Read timestamp for most recently posted feed item
        with file(filename, 'r') as settings:
            timestamp = int(settings.readline())

    timestamp = main(parser.parse_args(), timestamp, download_dir)

    # Record the most recent feed timestamp in a file
    if not SHOWRSS_DEBUG:
        with file(filename, 'w') as settings:
            settings.write(str(timestamp))


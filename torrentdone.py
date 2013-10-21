#!/usr/bin/env python

from datetime import datetime as dt
from hashlib import sha1
import re
import os


def parse_name(torrent_name):
    match = re.search('(.*)\.([sS]\d+)([eE]\d+)?', torrent_name)

    title = torrent_name
    season = 0
    episode = 0
    if match:
        t, s, e = match.groups()
        title = t.replace('.', ' ')
        try:
            season = int(s[1:])
            episode = int(e[1:])
        except:
            # Fall back to default values defined above
            pass

    return title, season, episode


def main():
    t_ver = os.environ.get('TR_APP_VERSION', '2.51')
    t_time = os.environ.get('TR_TIME_LOCALTIME', dt.now().strftime('%a %b %d %X %Y'))
    t_dir = os.environ.get('TR_TORRENT_DIR', os.path.expanduser('~'))
    t_hash = os.environ.get('TR_TORRENT_HASH', sha1(t_time).hexdigest())
    t_id = os.environ.get('TR_TORRENT_ID', '0')
    t_name = os.environ.get('TR_TORRENT_NAME', 'Show.Title.S00E00')

    with open(os.path.expanduser('~/showrss/torrent-done.log'), 'a') as f:
        f.write(t_time+'\n')  # Mon Dec 10 01:05:08 2012
        f.write(t_dir+'\n')   # /media/pi_server
        f.write(t_hash+'\n')  # 5ac55cf1b935291f6fc92ad7afd34597498ff2f7
        f.write(t_id+'\n')    # 16
                              # Pioneer.One.S01E01.REDUX.Xvid-VODO
        f.write('{0}, Season: {1}, Episode: {2}\n'.format(*parse_name(t_name)))
        f.write('\n')


if __name__ == '__main__':
    main()


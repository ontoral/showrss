#!/usr/bin/env python

import os

with file('/home/pi/showrss/torrent-done.log', 'a') as f:
    # f.write(os.environ.get('TR_APP_VERSION', 'TR_APP_VERSION')+'\n')
    # Version 2.52
    f.write(os.environ.get('TR_TIME_LOCALTIME', 'TR_TIME_LOCALTIME')+'\n')
    f.write(os.environ.get('TR_TORRENT_DIR', 'TR_TORRENT_DIR')+'\n')
    f.write(os.environ.get('TR_TORRENT_HASH', 'TR_TORRENT_HASH')+'\n')
    f.write(os.environ.get('TR_TORRENT_ID', 'TR_TORRENT_ID')+'\n')
    f.write(os.environ.get('TR_TORRENT_NAME', 'TR_TORRENT_NAME')+'\n')
    f.write('\n')


import re
from urllib import urlopen
from HTMLParser import HTMLParser

class TPBParser(HTMLParser):
    inRow = False
    row = None
    key = None
    data = None
    dataOpen = None
    peers = 'seeders'
    sizer = re.compile('.*Size ([^ ]*) ([^ ]*) .*')

    def __init__(self, url, maxSize, minSize=0):
        HTMLParser.__init__(self)
        self.minSize = minSize
        self.maxSize = maxSize
        self.torrents = []
        self.dataStack = []
        self.r5ts = re.compile('[ .](TS|R5)[ .]')

        self.add_feed(url)

    def add_feed(self, url):
        page = urlopen(url).read()
        self.feed(page)

    def handle_starttag(self, tag, attrs):
        adict = dict(attrs)
        if self.dataOpen:
            self.dataStack.append(tag)
        elif tag == 'tr':
            self.inRow = True
            self.row = {}
        elif tag == 'a' and self.inRow:
            self.data = ''
            if adict['href'].startswith('magnet:'):
                self.row['url'] = adict['href']
            elif adict.get('class', '') == 'detLink':
                self.dataOpen = tag
                self.key = 'title'
        elif tag == 'font' and adict.get('class', '') == 'detDesc':
            self.dataOpen = tag
            self.key = 'desc'
        elif self.inRow and tag == 'td' and adict.get('align', '') == 'right':
            self.dataOpen = tag
            self.key = self.peers
            self.peers = 'leechers' if self.peers == 'seeders' else 'seeders'

    def handle_data(self, data):
        if self.dataOpen:
            self.data += data

    def handle_endtag(self, tag):
        if self.dataStack:
            self.dataStack.pop()
        elif tag == 'tr':
            self.inRow = False
            if self.row:
                self.row['seeders'] = int(self.row['seeders'])
                self.row['leechers'] = int(self.row['leechers'])
                sz = re.findall(self.sizer, self.row['desc'])[0]
                factor = 1000000 if sz[1].startswith('Mi') else 1000000000
                self.row['size'] = float(sz[0]) * factor
                if self.row['size'] > self.maxSize or self.row['size'] < self.minSize:
                    print 'Skipping (size):', self.row['title']
                elif re.findall(self.r5ts, self.row['title']):
                    print 'Skipping (qual):', self.row['title']
                else:
                    self.torrents.append(self.row)
        elif self.data:
            self.row[self.key] = self.data
            self.dataOpen = None
            self.data = ''

    def handle_entityref(self, name):
        if self.dataOpen and name == 'nbsp':
            self.data += ' '
        

if __name__ == '__main__':
    tpbp = TPBParser('http://thepiratebay.se/top/203', 300000000)
    print len(tpbp.torrents), 'torrents'
    for torrent in tpbp.torrents:
        print torrent['title']
    tpbp = TPBParser('http://thepiratebay.se/top/201', 1700000000, 1000000000)
    print len(tpbp.torrents), 'torrents'
    for torrent in tpbp.torrents:
        print torrent['title']

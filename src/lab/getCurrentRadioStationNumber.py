'''
Created on 19 Jun 2013

@author: abednarski
'''
from urlparse import urlparse
from urlparse import parse_qs
import sys

def main(inputUrl):
    parsedUrl = urlparse(inputUrl)    
    urlQuery = parse_qs(parsedUrl.query)
    queryPlaylist = urlQuery['playlist']
    paylistNumber = queryPlaylist[0]
    return paylistNumber;
    
if __name__ == '__main__':
    playlistNumber = main(sys.argv[1])
    print playlistNumber
    sys.exit(0)
    
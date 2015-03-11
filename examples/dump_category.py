"""dump_category.py - utility script for wikitweets."""

import sys
import json
import getopt
import urllib
import urllib2

class ArticleFetchError(Exception):
    pass

def get_articles(base, category):
    regular_params = [
        ('cmtitle', "Category:%s" % (category)),
        ('action', 'query'),
        ('list', 'categorymembers'),
        ('cmlimit', '500'),
        ('cmprop', 'title|sortkey|timestamp'),
        ('format', 'json'),
    ]
    continue_params = []
    articles = []
    while True:
        qs = urllib.urlencode(regular_params + continue_params)
        url = base + '/w/api.php?' + qs
        req = urllib2.Request(url)
        try:
            json_data = urllib2.urlopen(req).read()
        except urllib2.URLError, e:
            raise ArticleFetchError(
                u'Error fetching URL ' + url + u' ' + unicode(e))
        try:
            data = json.loads(json_data)
        except ValueError, e:
            raise ArticleFetchError(
                u'Invalid JSON response from Wikipedia: %s' % (e,))
        articles += [article['title'] for article in data['query']['categorymembers']]
        if 'query-continue' in data:
            # how to fetch the next page of results
            continue_params = [(
                'cmcontinue',
                data['query-continue']['categorymembers']['cmcontinue'])]
            continue
        break
    return articles

def usage():
    return """%s - given a wikipedia category, dumps all article titles in it

Usage: %s [options] 'category name'

Options:
    -w, --wiki=W    Use the given wikipedia. Default: https://en.wikipedia.org
    -h, --help      Show this message and exit
""" % (sys.argv[0], sys.argv[0])

def main():
    base = 'https://en.wikipedia.org'
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'w:h', ['wiki=', 'help'])
        for o, a in opts:
            if o in ('-w', '--wiki'):
                base = a
            if o in ('-h', '--help'):
                print usage()
                return 0
        if len(args) != 1:
            raise getopt.GetoptError('category name required.')
        category = sys.argv[1]
    except getopt.GetoptError, e:
        print >> sys.stderr, e
        print >> sys.stderr, usage()
        return 2

    try:
        articles = get_articles(base, category)
    except ArticleFetchError, e:
        print >> sys.stderr, e
        return 1
    for article in articles:
        print article

if __name__ == '__main__':
    sys.exit(main())

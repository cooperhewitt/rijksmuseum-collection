#!/usr/bin/env python

import sys
import os
import os.path
import urllib2
import logging
import time

import xml.etree.ElementTree as ET
import unicodecsv

def crawl(p):

    for root, dirs, files in os.walk(p):

        if len(dirs) == 0:
            
            for f in files:
                path = os.path.join(root, f)
                path = os.path.realpath(path)
                yield path

        else:
            for d in dirs:
                path = os.path.join(root, d)
                crawl(path)

if __name__ == '__main__':

    import optparse
    import sys
    import csv

    parser = optparse.OptionParser()

    parser.add_option('-r', '--records', dest='records', action='store', help='...')
    parser.add_option('-o', '--outfile', dest='outfile', action='store', help='...')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='be chatty (default is false)')
        
    options, args = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    fh = open(options.outfile, 'w')
    writer = unicodecsv.UnicodeWriter(fh, ('rid', 'title', 'dates'))

    for p in crawl(options.records):

        if not p.endswith(".xml"):
            continue

        logging.info("process %s" % p)

        tree = ET.parse(p)
        root = tree.getroot()

        for rec in root.findall('.//{http://www.openarchives.org/OAI/2.0/}record'):

            row = {
                'rid': '',
                'title': '',
                'dates': ''
                }

            id = rec.find('{http://www.openarchives.org/OAI/2.0/}header/{http://www.openarchives.org/OAI/2.0/}identifier')
            id = id.text
            id = id.replace("oai:rijksmuseum.nl/collection:", "")

            row['rid'] = id

            dt = rec.find('.//{http://purl.org/dc/elements/1.1/}date')
            # logging.debug("dates: %s" % dt)

            if dt is not None:
                dt = dt.text
                row['dates'] = dt

            ttl = rec.find('.//{http://purl.org/dc/elements/1.1/}title')
            # logging.debug("title: %s" % ttl)

            if ttl is not None:
                ttl = ttl.text
                row['title'] = ttl

            logging.debug(row)
            writer.writerow(row)



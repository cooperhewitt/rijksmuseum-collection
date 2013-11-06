#!/usr/bin/env python

import os
import os.path
import urllib2
import logging
import time
import json
import multiprocessing

def crawl(p):

    for root, dirs, files in os.walk(p):

        if len(dirs) == 0:
            
            for f in files:
                path = os.path.join(root, f)
                yield path

        else:
            for d in dirs:
                path = os.path.join(root, d)
                crawl(path)

def compile(p):

    results = {}

    root = os.path.dirname(p)
    fname = os.path.basename(p)

    id = fname.replace(".jpg", "")
    palette = fname.replace(".jpg", "-palette.json")
    shannon = fname.replace(".jpg", "-shannon.json")

    palette = os.path.join(root, palette)
    shannon = os.path.join(root, shannon)

    results['id'] = id

    if os.path.exists(palette):

        fh = open(palette, 'r')
        data = json.load(fh)

        results['colour_avg'] = data['average']['colour']
        results['colour_avg_css3'] = data['average']['closest']

        i = 1

        for c in data['palette']:

            idx = i - 1

            results['colour_%s' % i] = data['palette'][idx]['colour']
            results['colour_%s_css3' % i] = data['palette'][idx]['closest']

            i += 1

    if os.path.exists(shannon):

        fh = open(shannon, 'r')
        data = json.load(fh)

        results['entropy'] = data['shannon']

    return results

if __name__ == '__main__':

    import optparse
    import sys
    import csv

    parser = optparse.OptionParser()

    parser.add_option('-I', '--images', dest='images', action='store', help='...')
    parser.add_option('-o', '--out', dest='out', action='store', help='...')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='be chatty (default is false)')
        
    options, args = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    total = 0
    current = 0

    counter = 0
    to_process = []

    fieldnames = [
        'id',
        'entropy',
        'colour_avg', 'colour_avg_css3',
        'colour_1', 'colour_1_css3',
        'colour_2', 'colour_2_css3',
        'colour_3', 'colour_3_css3',
        'colour_4', 'colour_4_css3',
        'colour_5', 'colour_5_css3'
        ]

    fh = open(options.out, 'w')
    writer = csv.DictWriter(fh, fieldnames=fieldnames)
    writer.writeheader()

    for p in crawl(options.images):

        if not p.endswith(".jpg"):
            continue

        row = compile(p)
        writer.writerow(row)

    logging.info("done")

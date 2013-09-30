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

if __name__ == '__main__':

    def write_json(data, path):

        logging.info("write: %s" % path)

        fh = open(path, 'w')
        json.dump(data, fh)
        fh.close()

    def extract_shannon(img):

        path = img.replace(".jpg", "-shannon.json")
    
        if os.path.exists(path):
            return

        try:
            req = "http://localhost:6521/json?path=%s" % img
            rsp = urllib2.urlopen(req)
    
            data = json.load(rsp)
            data['uri'] = path
    
            write_json(data, path)
        except Exception, e:
            logging.error("failed to extract shannon data for %s: %s" % (img, e))

    def extract_palette(img):

        path = img.replace(".jpg", "-palette.json")

        if os.path.exists(path):
            return

        try:
            req = "http://localhost:8000?path=%s" % img
            rsp = urllib2.urlopen(req)
        
            data = json.load(rsp)
            data['uri'] = path

            write_json(data, path)
        except Exception, e:
            logging.error("failed to extract shannon data for %s: %s" % (img, e))
            
    def dispatch(files):

        pool = multiprocessing.Pool()
        sh_jobs = pool.map_async(extract_shannon, files, chunksize=1)
        pl_jobs = pool.map_async(extract_palette, files, chunksize=1)
        pool.close()

        sleep = .05

        while True:

            remaining = 0
            done = True

            if not sh_jobs.ready():
                logging.debug('shannon jobs left: %s' % sh_jobs._number_left)
                remaining += sh_jobs._number_left
                done = False

            if not pl_jobs.ready():
                logging.debug('palette jobs left: %s' % pl_jobs._number_left)
                remaining += pl_jobs._number_left
                done = False

            if not done:
                tts =  (sleep * remaining) * 2
                logging.info("%s jobs remaining, sleep for %s seconds" % (remaining, tts))
                time.sleep(tts)
            else:
                break


    import ConfigParser
    import optparse
    import sys

    parser = optparse.OptionParser()

    parser.add_option('-I', '--images', dest='images', action='store', help='...')
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

    for p in crawl(options.images):
        total += 1

    for p in crawl(options.images):

        current += 1

        if not p.endswith(".jpg"):
            continue

        p = os.path.realpath(p)
        logging.info("[%s of %s] %s" % (current, total, p))

        to_process.append(p)
        counter += 1

        if counter < 100:
            continue

        dispatch(to_process)

        to_process = []
        counter = 0

    if len(to_process):
        dispatch(to_process)

    logging.info("done")

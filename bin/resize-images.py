#!/usr/bin/env python

import sys
import os
import os.path
import urllib2
import logging
import time

import shannon
import atk
import Image

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

def resize(p):

    logging.info("resize %s" % p)

    root = os.path.dirname(p)
    fname = os.path.basename(p)

    id = fname.replace(".jpg", "")

    small = fname.replace(".jpg", "_n.jpg")
    square = fname.replace(".jpg", "_sq.jpg")
    dither = fname.replace(".jpg", "_d.gif")

    small = os.path.join(root, small)
    square = os.path.join(root, square)
    dither = os.path.join(root, dither)

    if not make_small(p, small):
        logging.error("failed to make %s" % small)
        return False

    if not make_dithered(small, dither):
        logging.error("failed to make %s" % dither)
        return False

    if not make_square(p, square):
        logging.error("failed to make %s" % square)
        return False

    return True

def make_small(src, dest):

    if os.path.exists(dest):
        return True

    logging.info("make %s" % dest)

    cmd = "gm convert -quality 100 -resize 320 %s %s" % (src, dest)
    # logging.debug(cmd)

    os.system(cmd)
    
    return os.path.exists(dest)

def make_dithered(src, dest):

    if os.path.exists(dest):
        return True

    logging.info("make %s" % dest)

    img = Image.open(src)
    img = img.convert('L')
    sz = img.size

    tmp = atk.atk(sz[0], sz[1], img.tostring())
    new = Image.fromstring('L', sz, tmp)

    new = img.convert('1')
    new.save(dest)
    
    return os.path.exists(dest)

def make_square(src, dest):

    if os.path.exists(dest):
        return True

    logging.info("make %s" % dest)

    try:
        tmp = Image.open(src)

        shannon_region = shannon.sliced_shannon(tmp)
        logging.debug(shannon_region)
    except Exception, e:
        logging.error("failed to determine shannon region: %s" % e)
        return False

    if shannon_region['x'] > 100:
        x = shannon_region['x'] - 100
    else:
        x = shannon_region['x']
                
    if shannon_region['y'] > 100:
        y = shannon_region['y'] - 100
    else:
        y = shannon_region['y']
		
    mx = x + 300
    my = y + 300
	
    try:
        square = tmp.crop((x, y, mx, my))
        square.save(dest)
        
    except Exception, e:
        logging.error("failed to generate square crop for %s because %s" % (src, e))

    return os.path.exists(dest)

if __name__ == '__main__':

    import optparse
    import sys
    import csv

    parser = optparse.OptionParser()

    parser.add_option('-I', '--images', dest='images', action='store', help='...')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='be chatty (default is false)')
        
    options, args = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    for p in crawl(options.images):

        if not p.endswith(".jpg"):
            continue

        if p.endswith("_n.jpg"):
            continue

        if p.endswith("_sq.jpg"):
            continue

        if p.endswith("_d.gif"):
            continue

        resize(p)

    logging.info("done")

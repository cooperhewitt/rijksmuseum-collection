#!/usr/bin/env python

import sys
import os
import os.path
import urllib2
import httplib
import logging
import time

from boto.s3.connection import S3Connection
from boto.s3.key import Key

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

def transfer(bucket, path, force=False):

        fname = os.path.basename(path)

        aws_path = "%s/%s" % (bucket.name, fname)
        aws_url = 'http://s3.amazonaws.com/%s' % aws_path

        if not force:

            try:
                http_conn = httplib.HTTPConnection("s3.amazonaws.com")
                http_conn.request("HEAD", aws_url)
                rsp = http_conn.getresponse()

                if rsp.status == 200:
                    fname = os.path.basename(path)
                    logging.debug('HEAD returned 200, skipping %s' % fname)
                    return

            except Exception, e:
                logging.warning('HEAD requested failed: %s' % e)
                pass

        logging.info("copy %s to %s" % (path, aws_url))
        return True

        try:
            k = Key(bucket)
            k.key = fname

            k.set_contents_from_filename(path)

            # TEST ME... (20130212/straup)
            # max_age = 86400 * 30;
            # cache = "max-age=31556926,public" % max_age
            # headers = { 'Cache-Control': cache }
            # k.set_contents_from_filename(path, headers)
        
            mtime = os.path.getmtime(path)
            k.set_metadata('x-mtime', mtime)

            k.set_acl('public-read')

        except Exception, e:
            logging.error("failed to archive %s: %s" % (path, e))



if __name__ == '__main__':

    import optparse
    import ConfigParser

    parser = optparse.OptionParser()

    parser.add_option('-I', '--images', dest='images', action='store', help='...')
    parser.add_option('-c', '--config', dest='config', action='store', help='path to a config file containing AWS credentials, etc - see source code for a sample config')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='be chatty (default is false)')
        
    options, args = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    cfg = ConfigParser.ConfigParser()
    cfg.read(options.config)

    access_key = cfg.get('aws', 'access_key')
    access_secret = cfg.get('aws', 'access_secret')

    bucket_name = cfg.get('aws', 'bucket_name')

    conn = S3Connection(access_key, access_secret)
    bucket = conn.get_bucket(bucket_name)

    for p in crawl(options.images):

        if p.endswith("_n.jpg"):
            transfer(bucket, p)

        elif p.endswith("_sq.jpg"):
            transfer(bucket, p)

        elif p.endswith("_d.gif"):
            transfer(bucket, p)

        else:
            logging.debug("skip %s" % p)


    logging.info("done")

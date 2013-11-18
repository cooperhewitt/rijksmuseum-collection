#!/usr/bin/env python

import sys
import sqlite3
import csv
import unicodecsv
import logging
import re

if __name__ == '__main__':

    import optparse

    parser = optparse.OptionParser()

    parser.add_option('-c', '--csv-file', dest='csvfile', action='store', help='...')
    parser.add_option('-d', '--database', dest='database', action='store', help='...')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='be chatty (default is false)')
        
    options, args = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    fh = open(options.csvfile, 'r')
    reader = unicodecsv.UnicodeReader(fh)

    conn = sqlite3.connect(options.database)
    curs = conn.cursor()

    for row in reader:

        keys = []
        values = []
        update = []
        update_v = []

        for k, v in row.items():

            keys.append(k)
            values.append("'%s'" % v)

            if k != 'id':
                update.append("%s=?" % k)
                update_v.append(v)

        keys = ",".join(keys)
        values = ",".join(values)
        update = ",".join(update)

        update_v.append(row['id'])
        sql = "UPDATE objects SET %s WHERE id=?" % update


        # sql = "REPLACE INTO objects (%s) VALUES (%s)" % (keys, values)

        try:
            curs.execute(sql, update_v)
            conn.commit()
        except Exception, e:
            logging.error(sql)
            logging.error(e)
            sys.exit()




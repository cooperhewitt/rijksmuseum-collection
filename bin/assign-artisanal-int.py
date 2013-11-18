#!/usr/bin/env python

import sys
import csv
import logging

import ArtisanalInts

"""
Note: This is the simplest dumbest thing and does not (yet) consult a list of objects
that already have artisanal integers (20131118/straup)
"""

if __name__ == '__main__':

    import optparse
    import csv

    parser = optparse.OptionParser()

    parser.add_option('-i', '--infile', dest='infile', action='store', help='...')
    parser.add_option('-o', '--outfile', dest='outfile', action='store', help='...')
    parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='be chatty (default is false)')
        
    options, args = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    reader = csv.DictReader(open(options.infile, 'r'))
    writer = csv.writer(open(options.outfile, 'w'))

    start = False

    for row in reader:

        accession_number = row['id']

        if accession_number == 'RP-P-OB-55.097':
            start = True
            continue

        if not start:
            continue

        artisanal_integer, ignore = ArtisanalInts.get_brooklyn_integer()

        out = (accession_number, artisanal_integer)
        
        writer.writerow(out)
        print out

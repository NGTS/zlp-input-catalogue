#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Zero Level Pipeline catalog generation

Usage:
  ZLP_create_cat [options] --confmap=CONFMAP --filelist=FILELIST

Options:
  -h --help                                 Show help text
  -v, --verbose                             Print more text
  -o <OUTNAME>, --outname <OUTNAME>         Specify the name of the output catalog [default: catfile.fits]
  --c_thresh <C_THRESH>                     The detection threshold to use when defining the input [default: 7]
  --s_thresh <S_THRESH>                     The detection threshold to use when WCS solving images typically higher than when doing actual photometry [default: 7]
  -n <NPROC>, --nproc <NPROC>               Enable multithreading if you're analysing a lot of files at once
  --no-wcs                                  Do not solve each image for WCS.  However images must have a solution somehow
  --create-ell                              Produce ds9 region files for the final catalogue

This is the catalog generation tool, requires a filelist input. need to work on being selective on the files used in input.

"""

from docopt import docopt
import os
from .wcs_fitting import m_solve_images
from . import casutools
from .metadata import Metadata
from .ngts_logging import logger
from .version import __version__
from tempfile import NamedTemporaryFile
import sqlite3
from datetime import datetime
import tempfile

def ensure_cache(filelist, cache_directory_name='catcache'):
    cache_dir = os.path.join(
            os.getcwd(), cache_directory_name)
    if os.path.isdir(cache_dir):
        logger.info('Cache directory found')
    else:
        logger.warning("No cache directory found, solving first image to cache data")
        with open(filelist) as infile:
            first_filename = infile.readline().strip('\n')
        logger.warning('Using image {}'.format(first_filename))

        with tempfile.NamedTemporaryFile(prefix='dummywcs-', suffix='.fits') as tfile:
            name = tfile.name
            logger.warning('Extracting sources from first image')
            casutools.imcore(first_filename, name)

            tfile.seek(0)

            logger.warning('Finding dummy solution')
            casutools.wcsfit(first_filename, name)


def main():
    argv = docopt(__doc__, version=__version__)
    if argv['--verbose'] == True:
        logger.enable_debug()

    start = datetime.now()

    name = argv['--filelist']

    if not argv['--no-wcs']:
        logger.info("Astrometrically solving images")

        ensure_cache(name)
        extracted_metadata = m_solve_images(name, thresh=argv['--s_thresh'],
                nproc=int(argv['--nproc']) if argv['--nproc'] else None)
        Metadata(extracted_metadata).render()

    outstack_name = 'outstack.fits'
    outstackconf_name = 'outstackconf.fits'

    logger.info('Performing image stack')
    casutools.imstack(name, argv['--confmap'],
            outstack=outstack_name, outconf=outstackconf_name)
    logger.info('Extracting sources')
    casutools.imcore(outstack_name, argv['--outname'], threshold=argv['--c_thresh'],
            confidence_map=outstackconf_name,
            ellfile=argv['--create-ell'])

    logger.info('Catalogue complete')
    logger.info('Time taken: %s', datetime.now() - start)

if __name__ == '__main__':
    main()

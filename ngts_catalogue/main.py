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
  -n <NPROC>, --nproc <NPROC>               Enable multithreading if you're analysing a lot of files at once
  --outstack-name <outstack_name>           Output stack file name [default: outstack.fits]
  --outstackconf-name <outstackconf_name>   Output confidence map name [default: outstackconf.fits]

This is the catalog generation tool, requires a filelist input. need to work on being selective on the files used in input.

"""

from docopt import docopt
import os
from tempfile import NamedTemporaryFile
import sqlite3
from datetime import datetime
import tempfile

from . import casutools
from .ngts_logging import logger
from .version import __version__

def main():
    argv = docopt(__doc__, version=__version__)
    if argv['--verbose'] == True:
        logger.enable_debug()

    start = datetime.now()

    name = argv['--filelist']

    outstack_name = argv['--outstack-name']
    outstackconf_name = argv['--outstackconf-name']

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

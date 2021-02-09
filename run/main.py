import argparse
import configparser
import logging.config

from pathlib import Path

from .config import file_config
from .config import pyfile_config
from .run import run

def main(argv=None):
    """
    Download, parse/extract and write LIDO weight and balance message output.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog='run')
    parser.add_argument('pyfile', type=Path)
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, style='{')
    logger = logging.getLogger(__name__)

    conf = pyfile_config(args.pyfile)
    # run logging exceptions
    try:
        return run(conf)
    except:
        logger.exception('An exception occurred')

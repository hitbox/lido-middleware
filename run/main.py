import argparse
import configparser
import logging.config

from pathlib import Path

from .config import file_config
from .run import run

def main(argv=None):
    """
    Download, parse/extract and write LIDO weight and balance message output.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog='run')
    parser.add_argument('config', nargs='+', type=Path)
    args = parser.parse_args(argv)

    # RawConfigParser because format strings are expected
    cp = configparser.RawConfigParser()
    cp.read(args.config)

    # logging
    if all(section in cp for section in ['loggers', 'handlers', 'formatters']):
        logging.config.fileConfig(cp)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    conf = file_config(cp)
    # run logging exceptions
    try:
        return run(conf)
    except:
        logger.exception('An exception occurred')

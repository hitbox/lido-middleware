import argparse
import code
import logging.config
import time

from pathlib import Path

from .config import pyfile_config
from .run import run

def main(argv=None):
    """
    Command line interface to `run.run`.
    """
    parser = argparse.ArgumentParser(description=run.__doc__, prog='run')
    parser.add_argument('config_pyfile', type=Path)
    parser.add_argument(
        '--shell',
        action='store_true',
        help='Interactive shell after configured.')
    args = parser.parse_args(argv)

    # do logging in config or this takes over
    logging.basicConfig(level=logging.INFO, style='{')
    logger = logging.getLogger(__name__)

    conf = pyfile_config(args.config_pyfile)

    if args.shell:
        code.interact(local=conf)
    else:
        try:
            run(conf)
        except:
            logger.exception('An exception occurred')

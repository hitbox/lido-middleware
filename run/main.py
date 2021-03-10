import argparse
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
    parser.add_argument('pyfile', type=Path)
    parser.add_argument(
        '-w', '--watch', type=int, metavar='N',
        help='Run repeatedly every %(metavar)s seconds.')
    args = parser.parse_args(argv)

    # do logging in config or this takes over
    logging.basicConfig(level=logging.INFO, style='{')
    logger = logging.getLogger(__name__)

    conf = pyfile_config(args.pyfile)

    exit_code = 1
    try:
        while True:
            # run, logging exceptions
            exit_code = run(conf)
            if args.watch is None:
                break
            else:
                logger.debug('sleeping %s', args.watch)
                time.sleep(args.watch)
    except KeyboardInterrupt:
        pass
    return exit_code

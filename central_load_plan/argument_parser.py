import argparse
import os

from .constants import APPNAME

def argument_parser():
    """
    central_load_plan command line argument parser.
    """
    parser = argparse.ArgumentParser(
        description = 'Create Central Load Plan emails and files from XML files.',
        prog = APPNAME,
    )
    parser.add_argument('config', nargs='+')
    parser.add_argument('--dump-config',
        action = 'store_true',
        help = 'Dump config to stdout after parsing.',
    )
    parser.add_argument('--abort-on-error',
        action = 'store_true',
        help = 'Stop processing on exception.',
    )
    parser.add_argument('--test-smtp',
        action = 'store_true',
        help = 'Test SMTP connection and stop.',
    )
    parser.add_argument('--seconds',
        metavar = 'N',
        type = float,
        help = 'Run in continuous mode, every %(metavar)s seconds.',
    )
    return parser

def parse_and_validate_args(argv=None):
    parser = argument_parser()
    args = parser.parse_args(argv)

    # All given config files must exist.
    for fn in args.config:
        if not os.path.exists(fn):
            raise FileNotFoundError(fn)

    return args

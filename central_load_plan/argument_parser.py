import argparse

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
    parser.add_argument('--test-oracle',
        action = 'store_true',
        help = 'Test oracle connection and stop.',
    )
    parser.add_argument('--seconds',
        metavar = 'N',
        type = float,
        help = 'Run in continuous mode, every %(metavar)s seconds.',
    )
    return parser

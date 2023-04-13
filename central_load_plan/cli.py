import argparse

from . import main
from .constants import APPNAME

def parse_args(argv=None):
    """
    Process XML files into CLP email messages and send.
    """
    parser = argparse.ArgumentParser(
        description = main.run.__doc__,
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
    options = parser.parse_args(argv)
    return options

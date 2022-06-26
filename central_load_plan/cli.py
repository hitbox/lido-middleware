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
    options = parser.parse_args(argv)
    return options

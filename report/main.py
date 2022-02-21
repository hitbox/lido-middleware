import argparse
import configparser
import types

import utils

from .core import report

def main(argv=None):
    """
    Generate report of how pistol messages parse flight numbers.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog='report')
    parser.add_argument('config')
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)
    report_section = cp['report']
    config = types.SimpleNamespace(
        source_pickle = report_section['source_pickle'],
        message_filter = report_section['message_filter'],
        unique_key = report_section['unique_key'],
        extractor = utils._resolve(report_section['extractor']),
        ignore = report_section['ignore'],
        update_from = utils._resolve(report_section['update_from']),
        update_from_args = utils.getnumkeys(report_section, 'update_from_args'),
        outputfields = utils.getnumkeys(report_section, 'outputfield'),
    )

    report(config)

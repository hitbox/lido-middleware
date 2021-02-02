import argparse
import configparser
import logging.config

from pathlib import Path

from utils import _resolve

from .run import run

def main(argv=None):
    """
    Write LIDO weight and balance message file to FTP.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog='run')
    parser.add_argument('config', nargs='+', type=Path)
    args = parser.parse_args(argv)

    # RawConfigParser because format strings are expected
    cp = configparser.RawConfigParser()
    cp.read(args.config)

    if all(section in cp for section in ['loggers', 'handlers', 'formatters']):
        logging.config.fileConfig(cp)
    else:
        logging.basicConfig()
    logger = logging.getLogger(__name__)
    try:
        emailconf = cp['source']
        message_processor = _resolve(emailconf['message_processor'])
        schema = _resolve(emailconf['schema_class'])()
        ftpconf = cp['upload']
        return run(emailconf, message_processor, schema, ftpconf)
    except:
        logger.exception('An exception occurred')

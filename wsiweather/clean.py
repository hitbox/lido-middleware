import argparse
import configparser
import logging.config

from pathlib import Path

from .utils import is_glob

APPNAME = 'wsiweather.clean'
LOGGING_SECTIONS = set(['loggers', 'handlers', 'formatters'])

def realmain(patterns):
    """
    Remove files matching patterns.
    """
    logger = logging.getLogger(APPNAME)
    for pattern in patterns:
        logger.debug('globbing pattern %r', pattern)
        for path in glob.glob(pattern):
            path = Path(path)
            logger.debug('removing %r', path)
            path.unlink()

def main(argv=None):
    """
    Simple glob delete.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog=APPNAME)
    parser.add_argument('config', help='INI config for clean')
    args = parser.parse_args(argv)

    cp = configparser.RawConfigParser()
    cp.read(args.config)

    if LOGGING_SECTIONS.issubset(cp):
        logging.config.fileConfig(cp)

    appconf = cp[APPNAME]
    patterns = [appconf[key] for key in appconf if is_glob(key)]
    logger = logging.getLogger(APPNAME)
    try:
        realmain(patterns)
    except:
        logger.exception('An exception occurred')

if __name__ == '__main__':
    main()

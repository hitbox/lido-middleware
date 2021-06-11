import argparse
import configparser
import glob
import hashlib
import logging.config

from pathlib import Path

from . import pluck
from . import wxlmessage
from .output import get_output_path
from .schema import WSIWeatherSchema
from .utils import is_glob

APPNAME = 'wsiweather.run'
LOGGING_SECTIONS = set(['loggers', 'handlers', 'formatters'])

def hash1(path, text):
    """
    """
    # named with a one for future changes to hashing strategy
    string_bytes = str(path).encode('utf8') + str(text).encode('utf8')
    sha1 = hashlib.sha1(string_bytes)
    return sha1.hexdigest()

def realmain(patterns, output_template, copy_original, archive_path, uniquify_output):
    logger = logging.getLogger(APPNAME)
    archive_path = Path(archive_path)
    if archive_path.exists():
        with open(archive_path) as archive_file:
            archived = archive_file.read().splitlines()
    else:
        archived = []

    for pattern in patterns:
        logger.debug('globbing pattern %r', pattern)
        for path in glob.glob(pattern):
            path = Path(path)
            with open(path) as fp:
                text = fp.read()
                sha1hex = has1(path, text)
                if sha1hex in archived:
                    logger.debug('hash of %r found in archive, skipping', path)
                    continue

                logger.debug('processing %r', path)
                logger.debug('plucking')
                data = pluck.from_text(text)
                logger.debug('schema.load')
                data = schema.load(data)
                logger.debug('rendering')
                msg = wxlmessage.render(data)
                outpath = output_template.format(**data)
                logger.debug('writing rendered message to %r', outpath)
                print(msg)
                print(outpath)
                raise NotImplementedError

                # TODO: login ftp
                #       write archive
                #       copy original

def main(argv=None):
    """
    Process WSI files into Lido WXL messages.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog=APPNAME)
    parser.add_argument('config', help='INI config for run')
    args = parser.parse_args(argv)

    cp = configparser.RawConfigParser()
    cp.read(args.config)

    if LOGGING_SECTIONS.issubset(cp):
        logging.config.fileConfig(cp)

    schema = WSIWeatherSchema()
    appconf = cp[APPNAME]
    patterns = [appconf[key] for key in appconf if is_glob(key)]
    # rendered message output
    output_template = appconf['output_template']
    # TODO: move original destination
    copy_original = appconf['copy_original']
    archive_path = appconf['archive']
    uniquify_output = appconf.getboolean('uniquify_output')

    logger = logging.getLogger(APPNAME)
    try:
        realmain(patterns, output_template, copy_original, archive_path, uniquify_output)
    except:
        logger.exception('An exception occurred')

if __name__ == '__main__':
    main()

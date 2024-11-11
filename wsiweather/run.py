import argparse
import configparser
import glob
import hashlib
import logging.config
import shutil

from pathlib import Path

from fs import open_fs

from . import pluck
from . import wxlmessage
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

def realmain(
    patterns,
    schema,
    filename_template,
    output_fs,
    move_original,
    archive_path,
):
    logger = logging.getLogger(APPNAME)
    archive_path = Path(archive_path)
    if archive_path.exists():
        with open(archive_path) as archive_file:
            archived = archive_file.read().splitlines()
    else:
        archived = []

    for pattern in patterns:
        logger.debug('globbing pattern %r', pattern)
        for source_path in glob.glob(pattern):
            source_path = Path(source_path)
            with open(source_path) as fp:
                text = fp.read()
                sha1hex = hash1(source_path, text)
                if sha1hex in archived:
                    logger.debug('hash of %r found in archive, skipping', source_path)
                    continue

            logger.debug('processing %s', source_path)
            logger.debug('plucking')
            data = pluck.from_text(text)
            logger.debug('schema.load')
            data = schema.load(data)
            logger.debug('rendering')
            rendered_message = wxlmessage.render(data)

            filename = filename_template.format(**data)

            logger.debug('writing rendered message to %s, on %s', filename, output_fs)
            with open_fs(output_fs) as fs:
                fs.writetext(filename, rendered_message)

            logger.debug('mv %s %s', source_path, move_original)
            shutil.move(source_path, move_original)

            logger.debug('appending hash to archive %s', archive_path)
            with open(archive_path, 'a') as archive_file:
                archive_file.write(sha1hex + '\n')

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
    filename_template = appconf['filename_template']
    output_fs = appconf['output_fs']
    move_original = appconf['move_original']
    archive_path = appconf['archive']

    logger = logging.getLogger(APPNAME)
    try:
        realmain(
            patterns,
            schema,
            filename_template,
            output_fs,
            move_original,
            archive_path,
        )
    except:
        logger.exception('An exception occurred')

if __name__ == '__main__':
    main()

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

APPNAME = Path(__file__).parent.name
LOGGING_SECTIONS = set(['loggers', 'handlers', 'formatters'])

def is_glob(key):
    return key.startswith('glob') and key[-1].isdigit()

def hash1(path, text):
    """
    """
    string_bytes = str(path).encode('utf8') + str(text).encode('utf8')
    sha1 = hashlib.sha1(string_bytes)
    return sha1.hexdigest()

def main(argv=None):
    """
    Process WSI files into Lido WXL messages.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog=APPNAME)
    parser.add_argument('config')
    args = parser.parse_args(argv)

    cp = configparser.RawConfigParser()
    cp.read(args.config)

    if LOGGING_SECTIONS.issubset(cp):
        logging.config.fileConfig(cp)

    schema = WSIWeatherSchema()
    appconf = cp[APPNAME]
    patterns = [appconf[key] for key in appconf if is_glob(key)]
    output_template = appconf['output_template']
    archive_path = Path(appconf['archive'])
    uniquify_output = appconf.getboolean('uniquify_output')

    if archive_path.exists():
        with open(archive_path) as archive_file:
            archived = archive_file.read().splitlines()
    else:
        archived = []

    for pattern in patterns:
        for path in glob.glob(pattern):
            path = Path(path)
            with open(path) as fp:
                text = fp.read()
                sha1hex = has1(path, text)
                if sha1hex in archived:
                    continue

                data = pluck.from_text(text)
                data = schema.load(data)
                msg = wxlmessage.render(data)
                outpath = output_template.format(**data)
                print(msg)
                print(outpath)

                # TODO: write archive

if __name__ == '__main__':
    main()

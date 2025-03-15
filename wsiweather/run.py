import argparse
import hashlib
import io
import logging
import os
import shutil

import wsiweather.config
import wsiweather.pluck
import wsiweather.wxlmessage

from wsiweather.constants import APPNAME
from wsiweather.schema import WSIWeatherSchema
from wsiweather.utils import is_glob

def hash1(path, text):
    """
    """
    # named with a one for future changes to hashing strategy
    string_bytes = str(path).encode('utf8') + str(text).encode('utf8')
    sha1 = hashlib.sha1(string_bytes)
    return sha1.hexdigest()

def run(config, logger):
    """
    Process new weather files from configuration.
    """
    # Load archived hashes.
    archive = set()
    if os.path.exists(config.archive_path):
        with open(config.archive_path, 'r') as archive_file:
            for archive_line in archive_file:
                archive.add(archive_line.strip())

    # Process weather files.
    schema = WSIWeatherSchema()
    for source_name, source in config.sources.items():
        for source_path in source.paths():
            # Get text of source file and check archive to skip.
            with open(source_path) as source_file:
                text = source_file.read()
                sha1hex = hash1(source_path, text)
                if sha1hex in archive:
                    continue

            # Deserialize data from source and create message.
            wsi_data = wsiweather.pluck.from_text(text)
            wsi_data = schema.load(wsi_data)
            message = wsiweather.wxlmessage.render(wsi_data)

            # Write message to client.
            remote_filename = config.output_filename.format(**wsi_data)
            message_bytes = io.BytesIO(message.encode('utf-8'))
            config.client.write(message_bytes, remote_filename)

            # Move processed file.
            shutil.move(source_path, config.move_original)

            # Archive hash of path and filename.
            with open(config.archive_path, 'a') as archive_file:
                archive_file.write(sha1hex + '\n')
                archive.add(sha1hex)

            logger.info('processed: %s', source_path)

def main(argv=None):
    """
    Process WSI files into Lido WXL messages.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog=APPNAME)
    parser.add_argument('config', help='INI config for run')
    args = parser.parse_args(argv)

    # Parse configuration.
    config = wsiweather.config.parse(args.config)

    logger = logging.getLogger(APPNAME)
    try:
        run(config, logger)
    except:
        logger.exception('An exception occurred')

if __name__ == '__main__':
    main()

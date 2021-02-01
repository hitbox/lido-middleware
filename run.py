import argparse
import configparser
import csv
import ftplib
import io
import pickle

from datetime import date
from datetime import timedelta
from pathlib import Path

from imap_tools import AND
from imap_tools import MailBox

import lido

from utils import _resolve

def run(source_conf, message_processor, schema, upload_conf):
    """
    :param message_processor: callable to take email message and return loadplan data.
    """
    with MailBox(source_conf['host']) \
            .login(source_conf['username'],
                   source_conf['password']) as mailbox, \
            ftplib.FTP(upload_conf['host'],
                       upload_conf['username'],
                       upload_conf['password']) as upload_ftp:
        #
        yesterday = date.today() - timedelta(days=1)
        # messages since yesterday, from the pstl message sender
        pstl_since_yesterday = AND(
            from_ = source_conf['from_'],
            date_gte = yesterday,
        )
        limit = source_conf.get('limit')
        if limit is not None:
            limit = int(limit)
        messages = mailbox.fetch(pstl_since_yesterday, limit=limit, mark_seen=False)
        for message in messages:
            loadplan_data = message_processor(message)
            loadplan = schema.load(loadplan_data)
            lidomsg = lido.LIDOWeightBalanceMessage(loadplan)
            fp = io.BytesIO(str(lidomsg).encode('utf8'))
            pathfmt = upload_conf['filename']
            path = pathfmt.format(lidomsg=lidomsg)
            upload_ftp.storbinary('STOR ' + path, fp)

def main(argv=None):
    """
    Write new PSTL weight and balance messages from PSTL email.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args(argv)

    cp = configparser.RawConfigParser()
    cp.read(args.config)

    source_conf = cp['source']
    message_processor = _resolve(source_conf['message_processor'])
    schema = _resolve(source_conf['schema_class'])()
    upload_conf = cp['upload']

    run(source_conf, message_processor, schema, upload_conf)

if __name__ == '__main__':
    main()

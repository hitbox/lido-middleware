import argparse
import configparser
import ftplib
import io
import urllib

from datetime import date
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from pprint import pprint

from imap_tools import AND
from imap_tools import MailBox

import lido
import pistol

from utils import _resolve

def run(source_conf, message_processor, schema, upload_conf):
    """
    :param message_processor: callable to take email message and return loadplan data.
    """
    #
    runlog_path = Path(__file__).parent / f'instance/runlog/run.py.{datetime.now():%Y-%m-%d %H%M%S}.log'
    # messages since yesterday, from the pstl message sender
    since_yesterday_from = AND(
        from_ = source_conf['from_'],
        date_gte = date.today() - timedelta(days=1), # yesterday
    )
    pathfmt = upload_conf['pathfmt']
    with open(runlog_path, 'w') as runlog_fp, \
            MailBox(source_conf['host']) \
                .login(source_conf['username'],
                       source_conf['password']) as mailbox, \
            ftplib.FTP(upload_conf['host'],
                       upload_conf['username'],
                       upload_conf['password']) as upload_ftp:
        limit = source_conf.get('limit')
        if limit is not None:
            limit = int(limit)

        print('source_conf:', file=runlog_fp)
        pprint(source_conf, stream=runlog_fp)
        print(f'message_processor: {message_processor}', file=runlog_fp)
        print(f'schema: {schema}', file=runlog_fp)
        pprint(upload_conf, stream=runlog_fp)

        messages = mailbox.fetch(
            since_yesterday_from, limit=limit, mark_seen=False)
        for message in messages:
            print('message:', file=runlog_fp)
            print(message.subject, file=runlog_fp)
            print('\n'.join(message.text.splitlines()), file=runlog_fp)
            #
            fn = message.date.strftime('%Y-%m-%d %H%M%S') + message.subject.replace('/', '')
            email_path = Path(__file__).parent / 'instance/emailcopies' / urllib.parse.quote(message.subject)
            #
            loadplan_data = message_processor(message)
            loadplan = schema.load(loadplan_data)
            lidomsg = lido.LIDOWeightBalanceMessage(loadplan)
            fp = io.BytesIO(str(lidomsg).encode('utf8'))
            path = pathfmt.format(lidomsg=lidomsg)
            upload_ftp.storbinary('STOR ' + path, fp)
            #
            print('lido message string:', file=runlog_fp)
            print(str(lidomsg), file=runlog_fp)

def main(argv=None):
    """
    Write LIDO weight and balance message file to FTP.
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

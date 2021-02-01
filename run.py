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
import pistol.parse
import pistol.schema

def run(pistol_config, upload_config):
    with MailBox(pistol_config['host']) \
            .login(pistol_config['username'],
                   pistol_config['password']) as mailbox, \
            ftplib.FTP(upload_config['host'],
                       upload_config['username'],
                       upload_config['password']) as upload_ftp:
        #
        yesterday = date.today() - timedelta(days=1)
        # messages since yesterday, from the pstl message sender
        pstl_since_yesterday = AND(
            from_ = pistol_config['from_'],
            date_gte = yesterday,
        )
        # XXX: limit 1
        messages = mailbox.fetch(pstl_since_yesterday, limit=1, mark_seen=False)
        for msg in messages:
            print(msg.text, file=open('run_last_msg.txt', 'w'))
            loadplan_data = pistol.parse.loadplan_from_text(msg.text)
            loadplan = pistol.schema.LoadPlanSchema().load(loadplan_data)
            lidowb = lido.LIDOWeightBalanceMessage(loadplan)
            lidowb_msg = str(lidowb)
            print(lidowb)

            upload_ftp.cwd(upload_config['directory'])
            fp = io.BytesIO(lidowb_msg.encode('utf8'))
            upload_ftp.storbinary('STOR ' upload_config['filename'], fp)
            print('written')

def main(argv=None):
    """
    Write new PSTL weight and balance messages from PSTL email.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    pistol_config = cp['pistol']
    upload_config = cp['upload']

    run(pistol_config, upload_config)

if __name__ == '__main__':
    main()

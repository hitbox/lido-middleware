import argparse
import configparser

from imap_tools import MailBox
from imap_tools import OR
from imap_tools import AND

def download_emails(options):
    cp = configparser.ConfigParser()
    cp.read(options.config)

    mailbox_config = cp['mailbox']
    fetch_config = cp['fetch']
    download_config = cp['download']

    dest_fmt = download_config['dest_fmt']

    with MailBox(mailbox_config['host']) as mailbox:
        mailbox.login(mailbox_config['username'], mailbox_config['password'])
        criteria = eval(fetch_config['criteria_source'])
        messages = mailbox.fetch(
            criteria,
            limit=fetch_config.getint('limit'),
            mark_seen=False,
            reverse=True,
        )
        for msg in messages:
            dest = dest_fmt.format(msg=msg)
            print(dest)

def main(argv=None):
    """
    Development utilities for pistol middleware
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    subparsers = parser.add_subparsers()
    sp = subparsers.add_parser('download-emails')
    sp.add_argument('config')
    sp.set_defaults(func=download_emails)
    args = parser.parse_args(argv)

    func = args.func
    del args.func
    func(args)

if __name__ == '__main__':
    main()

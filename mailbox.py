import argparse
import code
import configparser
import pickle
import sys

from datetime import date
from datetime import timedelta
from pathlib import Path

from imap_tools import MailBox
from imap_tools import AND

from run.config import pyfile_config

def main(argv=None):
    """
    Browse mailbox in interactive interpreter.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog='mailbox')
    parser.add_argument('host')
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('--date_gte', type=date.fromisoformat)
    parser.add_argument('from_')
    #
    args = parser.parse_args(argv)

    if not args.date_gte:
        args.date_gte = date.today() - timedelta(days=1)

    with MailBox(args.host) as mailbox:
        mailbox.login(args.username, args.password)
        query = AND(
            date_gte = args.date_gte,
            from_ = args.from_,
        )
        messages = list(mailbox.fetch(query, mark_seen=False))
        code.interact(
                local = dict(
                    mailbox = mailbox,
                    messages = messages,
                )
            )

if __name__ == '__main__':
    main()

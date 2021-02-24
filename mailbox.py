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

def update_on_key(d, other):
    for k in d:
        if k in other:
            d[k] = other[k]

def criteria_from_section(section):
    criteria = dict()
    for key, value in section.items():
        if key.startswith('criteria_'):
            keyword = key[len('criteria_'):]
            try:
                value = eval(value, dict(date=date, timedelta=timedelta))
            except (NameError, SyntaxError):
                pass
            criteria[keyword] = value
    return criteria

def main(argv=None):
    """
    Small utility to save and browse mailboxes.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog='mailbox')
    subparsers = parser.add_subparsers(dest='subcommand', required=True)
    # save
    save_parser = subparsers.add_parser('save', help='Save/download a mailbox.')
    save_parser.add_argument('config', nargs='+')
    # browse
    browse_parser = subparsers.add_parser('browse', help='Browse mailbox in interactive interpreter.')
    browse_parser.add_argument('config', nargs='+')
    #
    args = parser.parse_args(argv)

    cp = configparser.RawConfigParser()
    cp.read(args.config)

    config = dict(
        host = None,
        username = None,
        password = None,
        limit = None,
        reverse = None,
        mark_seen = False,
        bulk = False,
        output = None,
    )
    update_on_key(config, cp['mailbox'])
    criteria_kwargs = dict()
    criteria_kwargs.update(criteria_from_section(cp['mailbox']))
    if criteria_kwargs:
        config['criteria'] = AND(**criteria_kwargs)
    else:
        config['criteria'] = None

    if isinstance(config['bulk'], str):
        config['bulk'] = config['bulk'].lower().strip() in ('1', 'yes', 'y', 'true')
    if config['limit']:
        config['limit'] = int(config['limit'])
    if config['reverse']:
        config['reverse'] = bool(config['reverse'])

    if args.subcommand == 'save':
        with MailBox(config['host']) as mailbox:
            mailbox.login(config['username'], config['password'])
            messages = mailbox.fetch(
                config['criteria'],
                limit = config['limit'],
                mark_seen = config['mark_seen'],
                bulk = config['bulk'])
            with open(config['output'], 'wb') as output_file:
                pickle.dump(list(messages), output_file)
    elif args.subcommand == 'browse':
        mailbox = MailBox(config['host'])
        mailbox.login(config['username'], config['password'])
        messages = list(
            mailbox.fetch(
                config['criteria'],
                limit = config['limit'],
                mark_seen = config['mark_seen'],
                bulk = config['bulk']))
        code.interact(
                local = dict(
                    mailbox = mailbox,
                    messages = messages,
                )
            )

if __name__ == '__main__':
    main()

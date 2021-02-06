import argparse
import configparser
import pickle
import sys

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
            criteria[keyword] = value
    return criteria

def main(argv=None):
    """
    Small utility to save mailboxes.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog='mailbox')
    subparsers = parser.add_subparsers(dest='subcommand', required=True)
    save_parser = subparsers.add_parser('save', help='Save/download a mailbox.')
    save_parser.add_argument('config', nargs='+')
    args = parser.parse_args(argv)

    cp = configparser.RawConfigParser()
    cp.read(args.config)

    config = dict(
        host = None,
        username = None,
        password = None,
        limit = None,
        mark_seen = False,
        bulk = False,
        output = None,
    )
    update_on_key(config, cp['mailbox'])
    criteria_kwargs = dict()
    criteria_kwargs.update(criteria_from_section(cp['mailbox']))
    config['criteria'] = AND(**criteria_kwargs)

    if isinstance(config['bulk'], str):
        config['bulk'] = config['bulk'].lower().strip() in ('1', 'yes', 'y', 'true')
    if config['limit']:
        config['limit'] = int(config['limit'])

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

if __name__ == '__main__':
    main()

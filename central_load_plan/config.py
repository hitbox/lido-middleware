import configparser
import logging.config
import os
import smtplib

from types import SimpleNamespace

from . import rendering
from .constants import APPNAME
from .schema import oracleconfschema
from .schema import smtpconfschema
from .utils import keyed_sections

class ConfigError(Exception):
    """
    Error raised by configuration parsing and checking.
    """

def raise_for_exists(path):
    if not os.path.exists(path):
        raise ConfigError('Path does not exist, %r' % path)

def raise_for_absolue_and_exists(path):
    if not os.path.isabs(path):
        raise ConfigError('Path is not absolute, %r' % path)
    raise_for_exists(path)

def raise_for_split_path(path):
    head = path
    while True:
        if os.path.exists(head):
            # good, found left side of path that exists
            break
        head, _ = os.path.split(head)
        if not head:
            raise ConfigError('split path not found')

def process(config_filename):
    """
    Parse config file, setup logging if configured (basic config otherwise),
    and return namespace config for CLPApp.
    """
    cp = configparser.RawConfigParser()
    cp.read(config_filename)

    if all(key in cp for key in ['loggers', 'formatters', 'handlers']):
        logging.config.fileConfig(cp)
    else:
        logging.basicConfig(level=logging.INFO)

    appconf = cp[APPNAME]

    required_sections = [
        APPNAME,
        'smtp',
        'oracle',
    ]
    for key in required_sections:
        if key not in cp:
            raise ConfigError('Missing section key, %r' % key)

    required_appconf = [
        'source_glob',
        'move_to',
    ]
    for key in required_appconf:
        if key not in appconf:
            raise ConfigError('Missing required key, %r' % key)

    # if given, value must be a path that exists
    if 'exception_move_to' in appconf:
        path = appconf['exception_move_to']
        raise_for_exists(path)

    appconf_data = SimpleNamespace(
        source_glob = appconf['source_glob'],

        # format strings for where to move source file after processing
        # mkdir is a separate option to avoid confusion with filenames, i.e.,
        # *NOT* accidentally creating a directory with the filename in it
        move_to = appconf['move_to'].strip(),
        move_to_mkdir = appconf['move_to_mkdir'].strip(),

        exception_move_to = appconf.get('exception_move_to'),
        ignore_crewmembers = appconf.getboolean('ignore_crewmembers'),
        dry_run = appconf.getboolean('dry', fallback=False),
        abort_on_error = appconf.getboolean('abort_on_error', fallback=False),
        smtpconf = smtpconfschema.load(cp['smtp']),
        # emailconf: airline code keyed dict of to-addresses and templates
        emailconf = keyed_sections(cp, 'emailmessage'),
        # file_output_conf
        file_output_conf = keyed_sections(cp, 'file_output'),
        dbconf = keyed_sections(cp, 'oracle', func=oracleconfschema.load),
    )

    # all paths must be absolute and exist
    attrs = [
        'source_glob',
        'exception_move_to',
    ]
    for attr in attrs:
        path = getattr(appconf_data, attr)
        if attr == 'source_glob':
            # strip wildcard from glob
            # NOTE: would need to do more work to strip /**/* recursive globs
            path = os.path.dirname(path)
        raise_for_absolue_and_exists(path)

    # format string should eventually devolve to a path that exists
    for attr in ['move_to', 'move_to_mkdir']:
        raise_for_split_path(getattr(appconf_data, attr))

    # raise for email template paths exist
    for item in appconf_data.emailconf.items():
        airline_iata_code, airline_email_conf = item
        rendering.env.get_template(airline_email_conf['template'])

    # raise for smtp
    with smtplib.SMTP(**appconf_data.smtpconf):
        pass

    return appconf_data

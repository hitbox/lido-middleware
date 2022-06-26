import configparser
import logging.config
import os

from types import SimpleNamespace

from .constants import APPNAME
from .schema import oracleconfschema
from .schema import smtpconfschema
from .utils import keyed_sections

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
            raise KeyError('Missing section key, %r' % key)

    required_appconf = [
        'source_glob',
        'move_to',
    ]
    for key in required_appconf:
        if key not in appconf:
            raise KeyError('Missing required key, %r' % key)

    # if given, value must be a path that exists
    if 'exception_move_to' in appconf:
        path = appconf['exception_move_to']
        if not os.path.exists(path):
            raise ValueError('Path does not exist, %r', path)

    appconf_data = SimpleNamespace(
        source_glob = appconf['source_glob'],
        move_to = appconf['move_to'].strip(),
        exception_move_to = appconf.get('exception_move_to'),
        ignore_crewmembers = appconf.getboolean('ignore_crewmembers'),
        smtpconf = smtpconfschema.load(cp['smtp']),
        # emailconf: airline code keyed dict of to-addresses and templates
        emailconf = keyed_sections(cp, 'emailmessage'),
        # file_output_conf
        file_output_conf = keyed_sections(cp, 'file_output'),
        dbconf = keyed_sections(cp, 'oracle', func=oracleconfschema.load),
    )

    return appconf_data

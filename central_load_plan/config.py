import configparser
import logging.config

from types import SimpleNamespace

from .constants import appname
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

    appconf = cp[appname]

    appconf_data = SimpleNamespace(
        source_glob = appconf['source_glob'],
        move_to = appconf['move_to'].strip(),
        move_to_on_schema_load_error = appconf.get('move_to_on_schema_load_error'),
        ignore_crewmembers = appconf.getboolean('ignore_crewmembers'),
        smtpconf = smtpconfschema.load(cp['smtp']),
        # emailconf: airline code keyed dict of to-addresses and templates
        emailconf = keyed_sections(cp, 'emailmessage'),
        # file_output_conf
        file_output_conf = keyed_sections(cp, 'file_output'),
        dbconf = keyed_sections(cp, 'oracle', func=oracleconfschema.load),
    )
    return appconf_data

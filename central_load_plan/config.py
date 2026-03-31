import configparser
import logging.config
import os

from types import SimpleNamespace

import central_load_plan.models

from . import rendering
from .constants import APPNAME
from .models import EFFZipReader
from .models import EmailOutput
from .models import GlobSource
from .models import NullArchive
from .models import PathArchive
from .models import XMLReader
from .schema import OracleConfSchema
from .schema import SMTPConfSchema
from .utils import keyed_sections

CONFIG_EVAL_CONTEXT = {
    'EFFZipReader': EFFZipReader,
    'EmailOutput': EmailOutput,
    'GlobSource': GlobSource,
    'NullArchive': NullArchive,
    'PathArchive': PathArchive,
    'XMLReader': XMLReader,
}

class ConfigError(Exception):
    """
    Error raised by configuration parsing and checking.
    """

def human_split(string):
    return string.replace(',', ' ').split()

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

def ensure_logging(cp):
    if all(key in cp for key in ['loggers', 'formatters', 'handlers']):
        logging.config.fileConfig(cp)
    else:
        logging.basicConfig(level=logging.INFO)

def raise_for_validation(cp):
    required_sections = [
        APPNAME,
        'smtp',
        'oracle',
    ]
    for key in required_sections:
        if key not in cp:
            raise ConfigError('Missing section key, %r' % key)

    # if given, value must be a path that exists
    appconf = cp[APPNAME]

    if 'exception_move_to' in appconf:
        path = appconf['exception_move_to']
        raise_for_exists(path)

def instance_from_section(section, context=None):
    """
    Instantiate from config section.
    """
    if context is None:
        context = CONFIG_EVAL_CONTEXT
    class_ = eval(section['class'], {}, context)
    args = eval(section.get('args', '()'))
    kwargs = eval(section.get('kwargs', '{}'))
    instance = class_(*args, **kwargs)
    return instance

def raise_for_config_data(appconf_data):
    # raise for email template paths exist
    for item in appconf_data.emailconf.items():
        airline_iata_code, airline_email_conf = item
        rendering.env.get_template(airline_email_conf['template'])

def process(config_filename):
    """
    Parse config file, setup logging if configured (basic config otherwise),
    and return namespace config for CLPApp.
    """
    cp = configparser.RawConfigParser()
    cp.read(config_filename)

    # Ensure logging is configured.
    ensure_logging(cp)

    # Raise for configuration.
    raise_for_validation(cp)

    # Determine config parser from version.
    config_version = cp[APPNAME].get('version', '')
    if config_version in ('', '0'):
        parser = process_original
    elif config_version == '1':
        parser = process_v1

    # Parse config into data for app.
    appconf_data = parser(cp)
    return appconf_data

def process_original(cp):
    appconf = cp[APPNAME]

    # Instantiate reader object.
    reader_suffix = appconf.get('reader')
    if not reader_suffix:
        # Use pluggable reader that emulates the original behavior.
        reader = central_load_plan.models.XMLReader()
    else:
        # Instantiate reader object from configuration.
        reader_section = cp['reader.' + reader_suffix]
        reader = instance_from_section(reader_section)

    # Instantiate source objects
    sources = []
    for source_suffix in human_split(appconf['sources']):
        source_section = cp['source.' + source_suffix]
        source = instance_from_section(source_section)
        sources.append(source)

    # Instantiate archive object
    archive_section = cp['archive.' + appconf['archive']]
    archive = instance_from_section(archive_section)

    # Ad-hoc force write file for from nested zip eff file.
    force_write_out = appconf.get('force_write_out')

    smtpconfschema = SMTPConfSchema()
    oracleconfschema = OracleConfSchema()

    appconf_data = SimpleNamespace(
        sources = sources,
        seconds = appconf.getfloat('seconds'),
        # Reader object
        reader = reader,
        # Archive
        archive = archive,
        # format strings for where to move source file after processing
        move_to = appconf.get('move_to', fallback=None),
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
        minimum_age = appconf.getfloat('minimum_age'),
        force_write_out = force_write_out,
        dbconf_fallback = keyed_sections(cp, 'fallback_oracle', func=oracleconfschema.load),
    )

    raise_for_config_data(appconf_data)

    return appconf_data

def process_v1(cp):
    appconf = cp[APPNAME]
    raise NotImplementedError

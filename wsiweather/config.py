import configparser
import logging.config
import os

from wsiweather.constants import APPNAME
from wsiweather.model import FTPClient
from wsiweather.model import Glob
from wsiweather.model import PathOutput

CONFIG_EVAL_CONTEXT = {
    'Glob': Glob,
    'FTPClient': FTPClient,
    'PathOutput': PathOutput,
}

class Config:
    """
    Configuration values required to process files.
    """

    def __init__(
        self,
        sources,
        client,
        output_filename,
        archive_path,
        move_original,
    ):
        self.sources = sources
        self.client = client
        self.output_filename = output_filename
        self.archive_path = archive_path
        self.move_original = move_original


def is_glob(key):
    return key.startswith('glob') and key[-1].isdigit()

def ensure_logging(cp):
    """
    Ensure logging is configured.
    """
    if set(['loggers', 'handlers', 'formatters']).issubset(cp):
        logging.config.fileConfig(cp)
    else:
        logging.basicConfig(level=logging.INFO)

def human_split(string):
    """
    Split a string on whitespace and optional commas.
    """
    return string.replace(',', ' ').split()

def instance_from_section(section):
    """
    Create an instance from a config section.
    """
    class_ = eval(section['class'], {}, CONFIG_EVAL_CONTEXT)
    args = eval(section.get('args', '()'), {}, CONFIG_EVAL_CONTEXT)
    kwargs = eval(section.get('kwargs', '()'), {}, CONFIG_EVAL_CONTEXT)
    instance = class_(*args, **kwargs)
    return instance

def instances_from_list(cp, string, prefix):
    """
    Generate instances from config sections, referenced by a human readable
    list of names.
    """
    suffixes = set()
    for suffix in human_split(string):
        if suffix in suffixes:
            raise ValueError(f'Duplicate name: {suffix}')
        section = cp[prefix + suffix]
        yield (suffix, instance_from_section(section))
        suffixes.add(suffix)

def parse(configs):
    """
    Parse the config files.
    """
    cp = configparser.RawConfigParser()
    cp.read(configs)

    # Configure logging.
    ensure_logging(cp)

    # Get values from config.
    appconf = cp[APPNAME]
    sources = dict(instances_from_list(cp, appconf['sources'], 'source.'))
    client = instance_from_section(cp['client.' + appconf['client']])
    archive_path = appconf['archive']
    output_filename = appconf['output_filename']
    move_original = appconf['move_original']

    # Raise for validation.
    if not os.path.exists(move_original):
        raise FileNotFoundError(
            f'Path to move files not found: {move_original}')

    result = Config(
        sources = sources,
        client = client,
        output_filename = output_filename,
        archive_path = archive_path,
        move_original = move_original,
    )
    return result

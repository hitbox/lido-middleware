import argparse
import configparser
import glob
import logging.config

from pprint import pprint

from .app import CLPApp
from .constants import appname
from .schema import oracleconfschema
from .schema import smtpconfschema
from .utils import keyed_sections

def main(argv=None):
    """
    Process XML files into CLP email messages and send.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('config', nargs='+')
    parser.add_argument('--dump-config',
        action = 'store_true',
        help = 'Dump config to stdout after parsing.',
    )
    parser.add_argument('--abort-on-error',
        action = 'store_true',
        help = 'Stop processing on exception.',
    )
    args = parser.parse_args(argv)

    cp = configparser.RawConfigParser()
    cp.read(args.config)

    if all(key in cp for key in ['loggers', 'formatters', 'handlers']):
        logging.config.fileConfig(cp)
    else:
        logging.basicConfig(level=logging.INFO)

    appconf = cp[appname]
    source_glob = appconf['source_glob']
    move_to = appconf['move_to'].strip()
    move_to_on_schema_load_error = appconf.get('move_to_on_schema_load_error')
    ignore_crewmembers = appconf.getboolean('ignore_crewmembers')
    smtpconf = smtpconfschema.load(cp['smtp'])
    # emailconf: airline code keyed dict of to-addresses and templates
    emailconf = keyed_sections(cp, 'emailmessage')
    # file_output_conf
    file_output_conf = keyed_sections(cp, 'file_output')
    dbconf = keyed_sections(cp, 'oracle', func=oracleconfschema.load)

    if args.dump_config:
        names = [
            'source_glob',
            'move_to',
            'move_to_on_schema_load_error',
            'ignore_crewmembers',
            'smtpconf',
            'emailconf',
            'file_output_conf',
            'dbconf',
        ]
        values = [
            source_glob,
            move_to,
            move_to_on_schema_load_error,
            ignore_crewmembers,
            smtpconf,
            emailconf,
            file_output_conf,
            dbconf,
        ]
        pprint(list(zip(names, values)))
        return

    clpapp = CLPApp(
        source_glob,
        move_to,
        move_to_on_schema_load_error,
        smtpconf,
        emailconf,
        file_output_conf,
        dbconf,
        ignore_crewmembers,
        abort_on_error = args.abort_on_error,
    )

    logger = logging.getLogger(appname)
    try:
        clpapp.run()
    except:
        logger.exception('Exception occurred during run')
        if args.abort_on_error:
            raise

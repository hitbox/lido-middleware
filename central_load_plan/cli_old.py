import argparse
import logging
import smtplib

from pprint import pprint

from . import config
from .app import CLPApp
from .argument_parser import argument_parser
from .constants import APPNAME

def _test_smtp(conf):
    with smtplib.SMTP(**conf):
        print(f'Connected SMTP {conf}')

def _test_oracle(company_confs):
    from .crewmember import get_engine
    for company_code, company_dbconf in company_confs.items():
        engine = get_engine(company_dbconf)
        with engine.connect():
            print(f'Connected {company_code} {engine}')

def run(argv=None):
    """
    Create Central Load Plan emails and files from XML files.
    """
    parser = argument_parser()
    options = parser.parse_args(argv)
    appconf = config.process(options.config)

    # flags that stop after processed
    if (
        options.dump_config
        or options.test_smtp
        or options.test_oracle
    ):
        if options.dump_config:
            pprint(appconf)

        if options.test_smtp:
            _test_smtp(appconf.smtpconf)

        if options.test_oracle:
            _test_oracle(appconf.dbconf)

        return

    clpapp = CLPApp(
        sources = appconf.sources,
        reader = appconf.reader,
        archive = appconf.archive,
        move_to = appconf.move_to,
        exception_move_to = appconf.exception_move_to,
        smtpconf = appconf.smtpconf,
        emailconf = appconf.emailconf,
        file_output_conf = appconf.file_output_conf,
        dbconf = appconf.dbconf,
        ignore_crewmembers = appconf.ignore_crewmembers,
        abort_on_error = appconf.abort_on_error,
        dry_run = appconf.dry_run,
        minimum_age = appconf.minimum_age,
        force_write_out = appconf.force_write_out,
        dbconf_fallback = appconf.dbconf_fallback,
    )
    clpapp.run()

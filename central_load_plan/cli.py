"""
central_load_plan/cli.py

Refactored CLI using pipeline architecture.
"""
import logging
import os
import smtplib

from configparser import RawConfigParser
from pprint import pprint

from . import config
from .argument_parser import argument_parser
from .argument_parser import parse_and_validate_args
from .constants import APPNAME

logger = logging.getLogger(__name__)

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
    Create Central Load Plan emails, files, and JSON from XML files.
    """
    clargs = parse_and_validate_args(argv)

    appconf = RawConfigParser()
    appconf.read(clargs.config)

    # Test flags that stop after processing
    if clargs.dump_config or clargs.test_smtp or clargs.test_oracle:
        if clargs.dump_config:
            pprint(vars(appconf))

        if clargs.test_smtp:
            _test_smtp(appconf.smtpconf)

        if clargs.test_oracle:
            _test_oracle(appconf.dbconf)

        return 0

    # Create and run pipeline
    pipeline = create_pipeline_from_config(appconf)

    try:
        results = list(pipeline.run(appconf.sources))

        # Summary
        total = len(results)
        errors = sum(1 for r in results if r.errors)
        success = total - errors

        logger.info(f'Pipeline complete: {success}/{total} successful')

        if errors > 0 and appconf.abort_on_error:
            return 1

        return 0

    except KeyboardInterrupt:
        logger.warning('Interrupted by user')
        return 130
    except Exception:
        logger.exception('Pipeline failed')
        return 1

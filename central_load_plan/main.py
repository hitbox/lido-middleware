import argparse
from pprint import pprint

from . import config
from .app import CLPApp

def run(options):
    """
    Create Central Load Plan emails and files from XML files.
    """
    appconf = config.process(options.config)

    if options.dump_config:
        pprint(appconf)
        return

    clpapp = CLPApp(
        appconf.source_glob,
        appconf.move_to,
        appconf.move_to_mkdir,
        appconf.exception_move_to,
        appconf.smtpconf,
        appconf.emailconf,
        appconf.file_output_conf,
        appconf.dbconf,
        appconf.ignore_crewmembers,
        abort_on_error = appconf.abort_on_error,
        dry_run = appconf.dry_run,
    )

    clpapp.run()

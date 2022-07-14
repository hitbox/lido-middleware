import argparse
from pprint import pprint

from . import config
from .app import CLPApp

def run(options):
    """
    Process XML files into CLP email messages and send.
    """
    appconf = config.process(options.config)

    if options.dump_config:
        pprint(appconf)
        return

    clpapp = CLPApp(
        appconf.source_glob,
        appconf.move_to,
        appconf.exception_move_to,
        appconf.smtpconf,
        appconf.emailconf,
        appconf.file_output_conf,
        appconf.dbconf,
        appconf.ignore_crewmembers,
        abort_on_error = options.abort_on_error,
    )

    clpapp.run()

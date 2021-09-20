import argparse
import configparser
import glob
import logging.config
import os
import shutil
import smtplib
import sys
import traceback
import xml.etree.ElementTree as ET

from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from . import crewmember
from . import email
from . import pluck
from .exception import CentralLoadPlanError
from .schema import ofpschema
from .schema import oracleconfschema
from .schema import smtpconfschema
from .utils import keyed_sections

appname = 'central_load_plan'

class CentralLoadPlanError(Exception):
    pass



def raise_for_path(p):
    if not Path(p).exists():
        raise CentralLoadPlanError('%r does not exist')

# NOTE: is this what OFP stands for?
# https://www.quora.com/Do-you-know-a-source-with-good-explanation-to-all-abbreviations-used-in-an-OFP-Operational-Flight-Plan
# OFP: Operational Flight Plan

class CLPApp:

    def __init__(
        self,
        source_glob,
        move_to,
        smtpconf,
        emailconf,
        dbconf,
    ):
        self.source_glob = source_glob
        self.move_to = Path(move_to)
        self.smtpconf = smtpconf
        self.emailconf = emailconf
        self.dbconf = dbconf
        self.logger = logging.getLogger(appname)

    def run(self):
        "Entry point for full run against configuration"
        for source in map(Path, glob.glob(self.source_glob)):
            # skip empty
            if source.stat().st_size == 0:
                self.logger.info('skipping empty file %s' % source.resolve())
                continue
            try:
                self.process_file(source)
            except KeyboardInterrupt:
                raise
            except:
                self.logger.exception('Exception occurred')

    def process_file(self, source):
        tree = ET.parse(source)
        root = tree.getroot()
        strdict = pluck.fromxml(root)
        data = ofpschema.load(strdict)
        # crew members
        data['crewmembers'] = crewmember.fromdata(self.dbconf, data).crewmembers
        # build email
        emailmessage = EmailMessage()
        airline_iata_code = data['airline_iata_code']
        emailconf = self.emailconf[airline_iata_code]
        # set from, to, subject, ..., all option values get a chance at
        # using the values from data to use in a format string
        for key, value in emailconf.items():
            emailmessage[key] = value.format(**data)
        plaintext = email.render(emailconf, data)
        html = f'<pre>{ plaintext }</pre>'
        emailmessage.set_content(plaintext)
        emailmessage.add_alternative(html, subtype='html')
        # move
        if self.move_to:
            dest = Path(self.move_to)
            if dest.exists():
                self.move_file(source, dest)
        # send email
        with smtplib.SMTP(**self.smtpconf) as smtp:
            smtp.send_message(emailmessage)
            self.logger.info('email sent to %r', emailmessage['to'])

    def move_file(self, source, dest):
        move_to_full = dest / source.name
        if move_to_full.exists():
            self.logger.info('removing %s', move_to_full.resolve())
            move_to_full.unlink()
        self.logger.info('moving original to %s', dest.resolve())
        shutil.move(source, dest)


def main(argv=None):
    """
    Process XML files into CLP email messages and send.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('config', nargs='+')
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
    smtpconf = smtpconfschema.load(cp['smtp'])
    emailconf = keyed_sections(cp, 'emailmessage')
    dbconf = keyed_sections(cp, 'oracle', func=oracleconfschema.load)

    clpapp = CLPApp(source_glob, move_to, smtpconf, emailconf, dbconf)

    logger = logging.getLogger(appname)
    try:
        clpapp.run()
    except:
        logger.exception('Exception occurred during run')

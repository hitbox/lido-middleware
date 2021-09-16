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

from collections import ChainMap
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from marshmallow import Schema
from marshmallow import fields

from . import crewmember
from . import email
from . import pluck
from . import schema
from .exception import CentralLoadPlanError

appname = 'central_load_plan'

class CentralLoadPlanError(Exception):
    pass


class SMTPConfSchema(Schema):
    host = fields.String()
    port = fields.Integer()


class OracleConfSchema(Schema):
    oracle_lib_dir = fields.String()
    drivername = fields.String()
    host = fields.String()
    port = fields.Integer()
    username = fields.String()
    password = fields.String()
    database = fields.String()


smtpconfschema = SMTPConfSchema()
oracleconfschema = OracleConfSchema()
ofpschema = schema.OperationalFlightPlanSchema()

def raise_for_path(p):
    if not Path(p).exists():
        raise CentralLoadPlanError('%r does not exist')

# NOTE: is this what OFP stands for?
# https://www.quora.com/Do-you-know-a-source-with-good-explanation-to-all-abbreviations-used-in-an-OFP-Operational-Flight-Plan
# OFP: Operational Flight Plan

def keyed_sections(cp, prefix, sep='_', func=None):
    """
    Loop configparser sections starting with `prefix + sep`, creating a dict
    keyed on text after `sep` with values of dicts of that section. If a
    section named `prefix` exists it will be used as a base dict for the more
    specific keyed sections.

    (ignore spaces between in section names)
    [prefix]
    c = 5

    [prefix sep key1]
    a = 1

    [prefix sep key2]
    b = 2

    ...

    {'key1': {'a': '1', 'c': '5'}, 'key2': {'b': '2', 'c': '5'}, ...}

    :param cp: a ConfigParser instance
    :param prefix: first part of section name
    :param sep: separator string between first and last part
    :param func: a callable called on the dict values, useful for coercing types
    """
    if prefix in cp:
        base = cp[prefix]
    else:
        base = {}

    if func is None:
        func = lambda x: x

    result = {
        secname.partition(sep)[2]: func(dict(ChainMap(cp[secname], base)))
        for secname in cp if secname.startswith(prefix + sep)
    }
    return result

class CLPApp:

    def __init__(
        self,
        source_glob,
        move_to,
        smtpconf,
        emailconf,
        oracleconf,
    ):
        self.source_glob = source_glob
        self.move_to = Path(move_to)
        self.smtpconf = smtpconf
        self.emailconf = emailconf
        self.oracleconf = oracleconf

    def run(self):
        logger = logging.getLogger(appname)
        for source in map(Path, glob.glob(self.source_glob)):
            # skip empty
            if source.stat().st_size == 0:
                logger.info('skipping empty file %s' % source.resolve())
                continue
            self.parse_xml(source)

    def parse_xml(self, source):
        logger = logging.getLogger(appname)
        try:
            tree = ET.parse(source)
        except ET.ParseError:
            logger.exception('An exception occurred parsing XML')
            raise
        else:
            self.final_process(source, tree)

    def move_file(self, source, dest):
        logger = logging.getLogger(appname)
        move_to_full = dest / source.name
        if move_to_full.exists():
            logger.info('removing %s', move_to_full.resolve())
            move_to_full.unlink()
        logger.info('moving original to %s', dest.resolve())
        shutil.move(source, dest)

    def final_process(self, source, tree):
        logger = logging.getLogger(appname)
        try:
            root = tree.getroot()
            strdict = pluck.fromxml(root)
            data = ofpschema.load(strdict)
            # crew members
            data['crewmembers'] = crewmember.fromdata(self.oracleconf, data).crewmembers
            # build email
            emailmessage = EmailMessage()
            airline_iata_code = data['airline_iata_code']
            emailconf = self.emailconf[airline_iata_code]
            for key, value in emailconf.items():
                emailmessage[key] = value.format(**data)
            plaintext = email.render_text(data)
            html = f'<pre>{ plaintext }</pre>'
            emailmessage.set_content(plaintext)
            emailmessage.add_alternative(html, subtype='html')
            #
            if self.move_to:
                self.move_file(source, self.move_to)
            # send email
            logger.info('sending email to %r', emailmessage['to'])
            with smtplib.SMTP(**self.smtpconf) as smtp:
                smtp.send_message(emailmessage)
        except:
            logger.exception(
                'An exception occurred while plucking XML and email sending')
            raise


def main(argv=None):
    """
    Process XML files into CLP email messages and send.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('--limit', type=int, help='Limit number of XML files to process.')
    parser.add_argument('config', nargs='+')
    args = parser.parse_args(argv)

    cp = configparser.RawConfigParser()
    cp.read(args.config)

    if all(key in cp for key in ['loggers', 'formatters', 'handlers']):
        logging.config.fileConfig(cp)

    appconf = cp[appname]
    source_glob = appconf['source_glob']
    move_to = appconf['move_to'].strip()
    smtpconf = smtpconfschema.load(cp['smtp'])
    emailconf = keyed_sections(cp, 'emailmessage')
    oracleconf = keyed_sections(cp, 'oracle', func=oracleconfschema.load)

    clpapp = CLPApp(source_glob, move_to, smtpconf, emailconf, oracleconf)

    logger = logging.getLogger(appname)
    try:
        clpapp.run()
    except:
        logger.exception('An exception occurred')
        raise

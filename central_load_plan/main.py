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
from pathlib import Path

from . import crewmember
from . import email
from . import pluck
from . import schema
from .exception import CentralLoadPlanError

appname = 'central_load_plan'

def raise_for_path(p):
    if not Path(p).exists():
        raise CentralLoadPlanError('%r does not exist')

def root2rendered(root, airline_dbconf):
    """
    Process XML root of OFP file into rendered email body text.
    """
    # NOTE: is this what OFP stands for?
    # https://www.quora.com/Do-you-know-a-source-with-good-explanation-to-all-abbreviations-used-in-an-OFP-Operational-Flight-Plan
    # OFP: Operational Flight Plan
    data = pluck.fromxml(root)
    data = schema.OperationalFlightPlanSchema().load(data)
    # hit database for crew members
    data['crewmembers'] = crewmember.fromdata(airline_dbconf, data).crewmembers
    # build emails
    body = email.render(data)
    return body

def realmain(
        source_glob,
        airline_dbconf,
        smtp_host,
        email_subject,
        send_to,
        from_addr,
        raise_on_error,
        move_to = None,
        limit = None
    ):
    """
    1. Process OFP XML files from `source_glob` into CLP email messages.
    2. Move the OFP XML file to `move_to`.
    3. Send CLP email.

    :param source_glob: xml source glob.
    :param airline_dbconf: airline code to database connection info for crewmembers.
    :param smtp_host: smtp host to use.
    :param email_subject: subject of email.
    :param send_to: deliver processed message to email address.
    :param from_addr: from address for email.
    :param move_to: destination directory to move after processing.
    :param limit: limit number of files to process.
    """
    logger = logging.getLogger(appname)
    n = 0
    for source_path in glob.glob(source_glob):
        source_path = Path(source_path)
        logger.info(source_path.resolve())
        if os.path.getsize(source_path) == 0:
            logger.info('skipping empty file')
            continue
        try:
            tree = ET.parse(source_path)
        except ET.ParseError:
            if raise_on_error:
                raise
            else:
                logger.exception('An exception occurred during XML parsing')
        else:
            # catch and log exceptions here so that the other files may be processed.
            try:
                # parse XML and build CLP message
                root = tree.getroot()
                body = root2rendered(root, airline_dbconf)
                email_message = EmailMessage()
                email_message.set_content(body)
                email_message['Subject'] = email_subject
                email_message['From'] = from_addr
                email_message['To'] = send_to
                # move source
                if move_to is not None:
                    move_to = Path(move_to)
                    move_to_full = Path(move_to) / source_path.name
                    if move_to_full.exists():
                        logger.info('removing %s', move_to_full.resolve())
                        move_to_full.unlink()
                    logger.info('moving original to %s', move_to.resolve())
                    shutil.move(source_path, move_to)
                # send email
                logger.info('sending email to %r', send_to)
                with smtplib.SMTP(smtp_host) as smtp_server:
                    smtp_server.send_message(email_message)
                n += 1
                if limit is not None and n == limit:
                    break
            except:
                if raise_on_error:
                    raise
                else:
                    logger.exception(
                        'An exception occurred during XML processing'
                        ' and email sending')

def _get_airline_dbconf(cp):
    """
    Pluck the "airline_" prefixed sections out and return a dictionary lookup
    table for database connections, for looking up crew members.
    """
    airline_dbconf = {}
    prefix = 'airline_'
    for section_name in cp:
        if section_name.startswith(prefix):
            airline_code = section_name[len(prefix):]
            airline_dbconf[airline_code] = cp[section_name]
    return airline_dbconf

def main(argv=None):
    """
    Process XML files into CLP email messages and send.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('--limit', type=int, help='Limit number of XML files to process.')
    parser.add_argument('config', nargs='+')
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    # NOTE: required logging config
    logging.config.fileConfig(cp)
    airline_dbconf = _get_airline_dbconf(cp)
    appconfig = cp[appname]

    source_glob = appconfig['source_glob']
    smtp_host = appconfig['smtp_host']
    email_subject = appconfig['email_subject']
    send_to = appconfig['send_to']
    from_addr = appconfig['from_addr']

    move_to = appconfig.get('move_to')
    limit = appconfig.getint('limit')
    if args.limit is not None:
        limit = args.limit

    raise_on_error = appconfig.getboolean('raise')

    if move_to is not None:
        raise_for_path(move_to)

    logger = logging.getLogger(appname)
    try:
        realmain(
            source_glob,
            airline_dbconf,
            smtp_host,
            email_subject,
            send_to,
            from_addr,
            raise_on_error,
            move_to = move_to,
            limit = limit,
        )
    except KeyboardInterrupt:
        pass
    except:
        if raise_on_error:
            raise
        else:
            logger.exception('An exception occurred')

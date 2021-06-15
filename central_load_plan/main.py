import argparse
import configparser
import glob
import logging.config
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

appname = 'central_load_plan'

def realmain(
        source_glob,
        airline_dbconf,
        move_to,
        smtp_host,
        email_subject,
        send_to,
        from_addr,
    ):
    """
    :param source_glob: xml source glob.
    :param airline_dbconf: airline code to database connection info for crewmembers.
    :param move_to: destination directory to move after processing.
    :param smtp_host: smtp host to use.
    :param email_subject: subject of email.
    :param send_to: deliver processed message to email address.
    :param from_addr: from address for email.
    """
    logger = logging.getLogger(appname)
    for source_path in glob.glob(source_glob):
        logger.info(source_path)
        source_path = Path(source_path)
        try:
            tree = ET.parse(source_path)
        except ET.ParseError:
            logger.exception('An exception occurred during XML parsing')
        except KeyboardInterrupt:
            break
        else:
            root = tree.getroot()
            data = pluck.fromxml(root)
            data = schema.OperationalFlightPlanSchema().load(data)
            # hit database for crew members
            data['crewmembers'] = crewmember.fromdata(airline_dbconf, data).crewmembers
            # build emails
            msg = EmailMessage()
            body = email.render(data)
            msg.set_content(body)
            msg['Subject'] = email_subject
            msg['From'] = from_addr
            msg['To'] = send_to
            #with smtplib.SMTP(smtp_host) as smtp_server:
            #    smtp_server.send_message(msg)
            #shutil.move(source_path, destination)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('config', nargs='+')
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    logging.config.fileConfig(cp)

    airline_dbconf = {}
    prefix = 'airline_'
    for section_name in cp:
        if section_name.startswith(prefix):
            airline_code = section_name[len(prefix):]
            airline_dbconf[airline_code] = cp[section_name]

    appconfig = cp[appname]

    source_glob = appconfig['source_glob']
    move_to = appconfig['move_to']
    smtp_host = appconfig['smtp_host']
    email_subject = appconfig['email_subject']
    send_to = appconfig['send_to']
    from_addr = appconfig['from_addr']

    logger = logging.getLogger(appname)
    try:
        realmain(
            source_glob,
            airline_dbconf,
            move_to,
            smtp_host,
            email_subject,
            send_to,
            from_addr,
        )
    except:
        logger.exception('An exception occurred')

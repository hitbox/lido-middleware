import datetime
import glob
import logging
import os
import shutil
import smtplib
import time
import xml.etree.ElementTree as ET

from datetime import date
from email.message import EmailMessage
from email.utils import formatdate
from email.utils import make_msgid
from pathlib import Path

from marshmallow import ValidationError

from . import crewmember
from . import pluck
from . import rendering
from .constants import APPNAME
from .exception import CentralLoadPlanError
from .schema import OperationalFlightPlanSchema
from .utils import move_for_exception
from .utils import path_format_data

# NOTE: is this what OFP stands for?
# https://www.quora.com/Do-you-know-a-source-with-good-explanation-to-all-abbreviations-used-in-an-OFP-Operational-Flight-Plan
# OFP: Operational Flight Plan

logger = logging.getLogger(APPNAME)

class CLPApp:

    def __init__(
        self,
        sources,
        reader,
        archive,
        move_to,
        exception_move_to,
        smtpconf,
        emailconf,
        file_output_conf,
        dbconf,
        ignore_crewmembers,
        abort_on_error = False,
        dry_run = False,
        minimum_age = None,
        force_write_out = None,
        dbconf_fallback = None,
    ):
        """
        :param sources:
            List of objects that generate source paths.
        :param reader:
            Object reads xml from whatever source and returns an element tree.
        :param archive:
            Object to check and save files as processed.
        :param move_to: move source files after processing.
        :param exception_move_to: path to move source on exception.
        :param smtpconf: smtplib.SMTP arguments dict.
        :param emailconf:
            dict of airline email configurations keyed on two-letter code,
            which map to another dict specifying the template and to-addresses.
        :param file_output_conf:
            dict of airline codes mapped to a template and an output format
            string, for writing files.
        :param dbconf: see crewmember module.
        :param ignore_crewmembers:
            skip downloading crewmembers data. this avoid hitting the databases.
        :param abort_on_error:
            do not continue processing files from source glob on exception.
        :param dry_run:
            avoid having any effect on the filesystem, emails are still sent.
        :param minimum_age:
            optional minimum age to process file.
        :param force_write_out:
            Force writing the nested XML from EFF ZIP.
        :param dbconf_fallback:
            Another database config to try if the first fails.
        """
        self.sources = sources
        self.reader = reader
        self.archive = archive
        self.move_to = move_to
        self.exception_move_to = exception_move_to
        self.smtpconf = smtpconf
        self.emailconf = emailconf
        self.file_output_conf = file_output_conf
        self.dbconf = dbconf
        self.ignore_crewmembers = ignore_crewmembers
        self.abort_on_error = abort_on_error
        self.dry_run = dry_run
        self.minimum_age = minimum_age
        self.force_write_out = force_write_out
        self.dbconf_fallback = dbconf_fallback

    def run(self):
        """
        Entry point for full run against configuration
        """
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        substitutions = {
            'today': today,
            'yesterday': yesterday,
            'tomorrow': tomorrow,
        }
        for source in self.sources:
            for path in source.paths(substitutions):
                if not self.archive.check(path):
                    self._run(path, substitutions)

    def _run(self, source_path, substitutions):
        # Continue if file is not empty and older than minimum_age.
        status = os.stat(source_path)
        if status.st_size == 0:
            logger.info(f'ignore empty {source_path}')
            return

        diff = abs(time.time() - status.st_mtime)
        if self.minimum_age is not None and diff <= self.minimum_age:
            # Skip file for minimum age.
            logger.info('ignoring %f for minimum age.', diff)
            return

        try:
            self.process_file(source_path, substitutions)
        except KeyboardInterrupt:
            # let user break
            raise
        except Exception as exc:
            if self.exception_move_to:
                move_for_exception(source_path, self.exception_move_to, exc)
            logger.exception('Exception occurred %r', source_path)
            if self.abort_on_error:
                raise

    def process_file(self, source_path, substitutions):
        """
        Extract data from source_path and process in all configured ways.

        :param source_path: path to source file as from glob.
        """
        # NOTE
        # - using default values for the benefit of format strings
        xml_data = pluck.default_data()
        logger.info('process_file: %s, xml_data=%r', source_path, xml_data)

        real_xml_name, xml_root = self.reader.read(source_path)
        xml_data.update(pluck.fromxml(xml_root))

        # deserialize
        ofpschema = OperationalFlightPlanSchema()
        xml_data = ofpschema.load(xml_data)

        # Add crew members from external database.
        if not self.ignore_crewmembers:
            crewmembers_obj = crewmember.fromdata(self.dbconf, xml_data, dbconfig_fallback=self.dbconf_fallback)
            xml_data['crewmembers'] = crewmembers_obj.crewmembers

        # Ad-hoc write to make archive files for JSON processing.
        if self.force_write_out:
            more_subs = substitutions.copy()
            more_subs['real_xml_name'] = real_xml_name
            force_write_out = self.force_write_out.format(**more_subs, **xml_data)
            force_write_out = os.path.normpath(force_write_out)

            os.makedirs(os.path.dirname(force_write_out), exist_ok=True)
            with open(force_write_out, 'wb') as force_write_file:
                tree = ET.ElementTree(xml_root)
                tree.write(force_write_file, encoding="utf-8", xml_declaration=True)
                logger.info('forced write: %s', force_write_out)

        self.send_email(xml_data)
        self.write_output_files(xml_data)
        if self.move_to:
            self.do_move_source(source_path, xml_data)
        self.archive.save(source_path)

    def do_move_source(self, source_path, xml_data):
        """
        If configured, move source file.
        :param source_path: path to a file.
        """
        # NOTE
        # - possibly called with empty xml_data
        fmtdata = path_format_data(source_path)
        fmtdata.update(xml_data)
        dest_path = self.move_to.format(**fmtdata)

        # ensure directory exists
        dest_dir, _dest_fn = os.path.split(dest_path)
        if not os.path.exists(dest_dir):
            # dirname of source_path to compare dir with dir
            logger.info('mkdir %r',
                os.path.relpath(dest_dir, os.path.dirname(source_path))
            )
            if not self.dry_run:
                os.makedirs(dest_dir)

        self.move_file(source_path, dest_path)

    def send_email(self, xml_data):
        """
        Send all emails according to config.
        """
        # build email
        emailmessage = EmailMessage()
        airline_iata_code = xml_data['airline_iata_code']
        airline_emailconf = self.emailconf[airline_iata_code]
        # set from, to, subject, ..., all option values get a chance at
        # using the values from xml_data to use in a format string
        for key, value in airline_emailconf.items():
            emailmessage[key] = value.format(**xml_data)
        emailmessage['Message-ID'] = make_msgid()
        template = airline_emailconf['template']
        logger.info('email template=%s', template)
        plaintext = rendering.render(template, xml_data)
        html = f'<pre>{ plaintext }</pre>'
        emailmessage.set_content(plaintext)
        emailmessage.add_alternative(html, subtype='html')
        # send email
        with smtplib.SMTP(**self.smtpconf) as smtp:
            if not self.dry_run:
                smtp.send_message(emailmessage)
                logger.info(
                    'email: %r to %r, message-id=%r',
                    emailmessage['subject'],
                    emailmessage['to'],
                    emailmessage['message-id'],
                )

    def write_output_files(self, xml_data):
        """
        Write all output files according to config.

        :param xml_data: dict of xml_data.
        """
        # Find file config that matches airline code.
        for airline_iata_code, fileconfig in self.file_output_conf.items():
            if xml_data['airline_iata_code'] == airline_iata_code:
                break
        else:
            raise CentralLoadPlanError('airline code not found from xml data.')

        template = fileconfig['template']
        logger.info('file output template=%s', template)
        contents = rendering.render(template, xml_data)
        output_format = fileconfig['output_format']
        filename = output_format.format(**xml_data)
        if not self.dry_run:
            with open(filename, 'w') as output_file:
                output_file.write(contents)
        logger.info(
            'file: %s',
            os.path.normpath(filename)
        )

    def move_file(self, source, dest):
        """
        Move `source` to `dest` raise if it exists.
        :param source: full absoulte path to source file.
        :param dest: full absolute path to destination directory.
        """
        if os.path.exists(dest):
            raise CentralLoadPlanError('file exists: %r', dest)
        logger.info(
            'move %s to %s',
            os.path.normpath(os.path.basename(source)),
            os.path.normpath(os.path.relpath(dest, os.path.dirname(source)))
        )
        if not self.dry_run:
            shutil.move(source, dest)

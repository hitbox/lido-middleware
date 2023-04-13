import datetime
import glob
import logging
import os
import shutil
import smtplib
import xml.etree.ElementTree as ET

from email.message import EmailMessage
from pathlib import Path

from marshmallow import ValidationError

from . import crewmember
from . import pluck
from . import rendering
from .constants import APPNAME
from .exception import CentralLoadPlanError
from .schema import ofpschema
from .utils import move_for_exception
from .utils import path_format_data

# NOTE: is this what OFP stands for?
# https://www.quora.com/Do-you-know-a-source-with-good-explanation-to-all-abbreviations-used-in-an-OFP-Operational-Flight-Plan
# OFP: Operational Flight Plan

class CLPApp:

    def __init__(
        self,
        source_glob,
        move_to,
        move_to_mkdir,
        exception_move_to,
        smtpconf,
        emailconf,
        file_output_conf,
        dbconf,
        ignore_crewmembers,
        abort_on_error = False,
        dry_run = False,
    ):
        """
        :param source_glob: source files glob.
        :param move_to: move source files after processing.
        :param move_to_mkdir:
            format string to ensure directory `move_to` refers to exists.
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
        """
        self.source_glob = source_glob
        self.move_to = move_to
        self.move_to_mkdir = move_to_mkdir
        self.exception_move_to = exception_move_to
        self.smtpconf = smtpconf
        self.emailconf = emailconf
        self.file_output_conf = file_output_conf
        self.dbconf = dbconf
        self.ignore_crewmembers = ignore_crewmembers
        self.abort_on_error = abort_on_error
        self.dry_run = dry_run
        self.logger = logging.getLogger(APPNAME)

    def run(self):
        """
        Entry point for full run against configuration
        """
        for source_path in glob.glob(self.source_glob):
            self._run(source_path)

    def _run(self, source_path):
        self.logger.info('process: %r', source_path)
        try:
            self.process_file(source_path)
        except KeyboardInterrupt:
            # let user break
            raise
        except Exception as exc:
            self.logger.exception('Exception occurred %r', source_path)
            if not self.dry_run:
                move_for_exception(source_path, self.exception_move_to, exc)
            if self.abort_on_error:
                raise

    def process_file(self, source_path):
        """
        Extract data from source_path and process in all configured ways.
        """
        # skip empty
        if os.stat(source_path).st_size == 0:
            self.logger.info(
                'skip empty file %r', os.path.abspath(source_path))
        else:
            xml_data = self._process_file(source_path)
            # emails and output files only applicable for non-empty files
            self.send_email(source_path, xml_data)
            self.write_output_files(source_path, xml_data)

        # want to move source if empty too
        self.do_move_source(source_path)

    def _process_file(self, source_path):
        # actually process source_path, the motivation of this method is
        # reducing indentation.
        tree = ET.parse(source_path)
        root = tree.getroot()
        strdict = pluck.fromxml(root)
        xml_data = ofpschema.load(strdict)
        # crew members
        if self.ignore_crewmembers:
            xml_data['crewmembers'] = []
        else:
            crewmembers_obj = crewmember.fromdata(self.dbconf, xml_data)
            xml_data['crewmembers'] = crewmembers_obj.crewmembers
        return xml_data

    def do_move_source(self, source_path):
        """
        If configured, move source file.
        :param source_path: path to a file.
        """
        if self.move_to:
            fmtdata = path_format_data(source_path)
            dest_path = self.move_to.format(**fmtdata)

            # if given, ensure directory exists
            if self.move_to_mkdir:
                dest_dir = self.move_to_mkdir.format(**fmtdata)
                if not os.path.exists(dest_dir):
                    # dirname of source_path to compare dir with dir
                    self.logger.info('mkdir %r',
                        os.path.relpath(dest_dir, os.path.dirname(source_path))
                    )
                    if not self.dry_run:
                        os.makedirs(dest_dir)

            self.move_file(source_path, dest_path)

    def send_email(self, source_path, xml_data):
        """
        Send all emails according to config.
        """
        # NOTE
        # - this gives the format strings from config the source_path but does
        #   not give it to the email templates.
        # build email
        emailmessage = EmailMessage()
        airline_iata_code = xml_data['airline_iata_code']
        airline_emailconf = self.emailconf[airline_iata_code]
        # set from, to, subject, ..., all option values get a chance at
        # using the values from xml_data to use in a format string
        for key, value in airline_emailconf.items():
            emailmessage[key] = value.format(source_path=source_path, **xml_data)
        plaintext = rendering.render(airline_emailconf['template'], xml_data)
        html = f'<pre>{ plaintext }</pre>'
        emailmessage.set_content(plaintext)
        emailmessage.add_alternative(html, subtype='html')
        # send email
        with smtplib.SMTP(**self.smtpconf) as smtp:
            smtp.send_message(emailmessage)
            self.logger.info(
                'email: %r to %r', emailmessage['subject'], emailmessage['to'])

    def write_output_files(self, source_path, xml_data):
        """
        Write all output files according to config.
        """
        # NOTE
        # - the email module could be renamed
        # - it is really just a template renderer
        # - only the filename format string gets the source_path
        for airline_iata_code, fileconfig in self.file_output_conf.items():
            if xml_data['airline_iata_code'] != airline_iata_code:
                continue
            template = fileconfig['template']
            contents = rendering.render(template, xml_data)
            output_format = fileconfig['output_format']
            filename = output_format.format(source_path=source_path, **xml_data)
            if not self.dry_run:
                with open(filename, 'w') as output_file:
                    output_file.write(contents)
            self.logger.info('file: %r', os.path.relpath(filename, source_path))

    def move_file(self, source, dest):
        """
        Move `source` to `dest` raise if it exists.
        :param source: full absoulte path to source file.
        :param dest: full absolute path to destination directory.
        """
        if os.path.exists(dest):
            raise CentralLoadPlanError('file exists: %r', dest)
        prefix = os.path.commonprefix([source, dest])
        self.logger.info(
            'move %r to %r',
            os.path.basename(source),
            os.path.relpath(dest, os.path.dirname(source))
        )
        if not self.dry_run:
            shutil.move(source, dest)

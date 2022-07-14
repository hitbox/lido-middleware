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
from . import email
from . import pluck
from .constants import APPNAME
from .schema import ofpschema
from .utils import move_for_exception

# NOTE: is this what OFP stands for?
# https://www.quora.com/Do-you-know-a-source-with-good-explanation-to-all-abbreviations-used-in-an-OFP-Operational-Flight-Plan
# OFP: Operational Flight Plan

class CLPApp:

    def __init__(
        self,
        source_glob,
        move_to,
        exception_move_to,
        smtpconf,
        emailconf,
        file_output_conf,
        dbconf,
        ignore_crewmembers,
        abort_on_error = False,
    ):
        """
        :param source_glob: source files glob.
        :param move_to: move source files after processing.
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
        """
        self.source_glob = source_glob
        self.move_to = move_to
        self.exception_move_to = exception_move_to
        self.smtpconf = smtpconf
        self.emailconf = emailconf
        self.file_output_conf = file_output_conf
        self.dbconf = dbconf
        self.ignore_crewmembers = ignore_crewmembers
        self.abort_on_error = abort_on_error
        self.logger = logging.getLogger(APPNAME)

    def run(self):
        """
        Entry point for full run against configuration
        """
        for source_path in glob.glob(self.source_glob):
            # source_path is as complete as was specified in config
            # if a full path was given, we get one back
            try:
                self.process_file(source_path)
            except KeyboardInterrupt:
                # let user break
                raise
            except Exception as e:
                self.logger.exception('Exception occurred')
                move_for_exception(source_path, self.exception_move_to, e)
                if self.abort_on_error:
                    raise

    def process_file(self, source_path):
        """
        Extract data from source_path and process in all configured ways.
        """
        # skip empty
        if os.stat(source_path).st_size == 0:
            self.logger.info(
                'skip email and file output for empty file %s'
                % os.path.abspath(source_path))
        else:
            tree = ET.parse(source_path)
            root = tree.getroot()
            strdict = pluck.fromxml(root)
            data = ofpschema.load(strdict)
            # store original source path for file output
            data['source_path'] = source_path
            # crew members
            if not self.ignore_crewmembers:
                crewmembers_obj = crewmember.fromdata(self.dbconf, data)
                data['crewmembers'] = crewmembers_obj.crewmembers
            else:
                data['crewmembers'] = []
            #
            self.send_email(data)
            self.write_output_files(data)

        # always do move
        self.do_move_source(source_path)

    def do_move_source(self, source_path):
        """
        If configured, move source file.
        """
        if (
            self.move_to
            and os.path.exists(self.move_to)
        ):
            self.move_file(source_path, self.move_to)

    def send_email(self, data):
        """
        Send all emails according to config.
        """
        # build email
        emailmessage = EmailMessage()
        airline_iata_code = data['airline_iata_code']
        airline_emailconf = self.emailconf[airline_iata_code]
        # set from, to, subject, ..., all option values get a chance at
        # using the values from data to use in a format string
        for key, value in airline_emailconf.items():
            emailmessage[key] = value.format(**data)
        plaintext = email.render(airline_emailconf['template'], data)
        html = f'<pre>{ plaintext }</pre>'
        emailmessage.set_content(plaintext)
        emailmessage.add_alternative(html, subtype='html')
        # send email
        with smtplib.SMTP(**self.smtpconf) as smtp:
            smtp.send_message(emailmessage)
            self.logger.info('email %r to %r', emailmessage['subject'], emailmessage['to'])

    def write_output_files(self, data):
        """
        Write all output files according to config.
        """
        for airline_iata_code, fileconfig in self.file_output_conf.items():
            if data['airline_iata_code'] != airline_iata_code:
                continue
            template = fileconfig['template']
            contents = email.render(template, data)
            output_format = fileconfig['output_format']
            filename = output_format.format(**data)
            with open(filename, 'w') as output_file:
                output_file.write(contents)
            self.logger.info('created %s', filename)

    def move_file(self, source, dest):
        """
        Move `source` to `dest` removing `dest` if it exists.
        :param source: full absoulte path to source file.
        :param dest: full absolute path to destination directory.
        """
        source_filename = os.path.basename(source)
        final = os.path.join(dest, source_filename)
        if os.path.exists(final):
            self.logger.info('removing %s', final)
            os.remove(final)
        self.logger.info('moving original to %s', final)
        shutil.move(source, final)

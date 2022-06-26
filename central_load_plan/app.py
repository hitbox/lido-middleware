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
        for source in glob.glob(self.source_glob):
            # skip empty
            if os.stat(source).st_size == 0:
                self.logger.info('skipping empty file %s' % source.resolve())
                continue
            try:
                self.process_file(source)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.logger.exception('Exception occurred')
                move_for_exception(source, self.exception_move_to, e)
                if self.abort_on_error:
                    raise

    def process_file(self, source):
        """
        Extract data from source and process in all configured ways.
        """
        tree = ET.parse(source)
        root = tree.getroot()
        strdict = pluck.fromxml(root)
        data = ofpschema.load(strdict)
        # store original source filename
        data['source_filename'] = source
        # crew members
        if not self.ignore_crewmembers:
            data['crewmembers'] = crewmember.fromdata(self.dbconf, data).crewmembers
        else:
            data['crewmembers'] = []
        #
        self.send_email(data)
        self.do_move_source(data)
        self.write_output_files(data)

    def do_move_source(self, data):
        """
        If configured, move source file.
        """
        if self.move_to:
            if os.path.exists(self.move_to):
                self.move_file(data['source_filename'], self.move_to)

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
        """
        move_to_full = os.path.join(dest, source.name)
        if move_to_full.exists():
            self.logger.info('removing %s', move_to_full.resolve())
            move_to_full.unlink()
        self.logger.info('moving original to %s', dest.resolve())
        shutil.move(source, dest)

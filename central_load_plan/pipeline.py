"""
central_load_plan/pipeline.py

Clean pipeline-based architecture for processing operational flight plans.
"""
import logging

logger = logging.getLogger(__name__)

class ProcessingContext:
    """
    Context for a single file being processed.
    """

    def __init__(self, source_path, xml_data, archive):
        self.source_path = source_path
        self.xml_data = xml_data
        self.archive = archive
        self.errors = []
        self.outputs_written = []

    def as_dict(self):
        return {
            'source_path': self.source_path,
            'xml_data': self.xml_data,
            'archive': self.archive,
            'errors': self.errors,
            'outputs_written': self.outputs_written,
        }


class Stage:
    """
    Base class for pipeline stages.
    """

    def process(self, context):
        """
        Process the context. Return True to continue, False to abort.

        Stages should catch their own exceptions and add them to context.errors
        if they want processing to continue.
        """
        raise NotImplementedError


class XMLParser(Stage):
    """
    Parse XML and deserialize to data.
    """

    def __init__(self, reader, schema):
        self.reader = reader
        self.schema = schema

    def process(self, context):
        """
        Read XML file, updating the context object with scraped data.
        """
        from . import pluck
        try:
            real_xml_name, xml_root = self.reader.read(str(context.source_path))
            xml_data = pluck.fromxml(xml_root)
            data = self.schema.load(xml_data)
            context.xml_data.update(data)
            logger.debug(f'Parsed XML from {context.source_path}')
            return True
        except Exception as e:
            logger.exception(f'Failed to parse XML: {context.source_path}')
            context.errors.append(e)
            return False


class AirlineCrewMemberEnricher(Stage):
    """
    Add crew members from database.
    """

    def __init__(self, mapping):
        self.mapping = mapping

    def process(self, context):
        from . import crewmember
        try:
            airline_code = context.xml_data['airline_iata_code']
            airline_dbconf = self.mapping.get(airline_code)
            dbconf = airline_dbconf['dbconf']
            dbconf_fallback = airline_dbconf['dbconf_fallback']
            crew_obj = crewmember.fromdata(
                dbconf,
                context.xml_data,
                dbconfig_fallback=dbconf_fallback
            )
            context.xml_data['crewmembers'] = crew_obj.crewmembers
            logger.debug(f'Added {len(crew_obj.crewmembers)} crew members')
            return True
        except Exception as e:
            logger.exception('Failed to fetch crew members')
            context.errors.append(e)
            # Continue anyway - crew members are optional
            context.xml_data['crewmembers'] = []
            return True


class EmailOutput(Stage):
    """
    Send email output.
    """

    def __init__(self, smtpconf, emailconf):
        self.smtpconf = smtpconf
        self.emailconf = emailconf

    def process(self, context):
        try:
            import smtplib
            from email.message import EmailMessage
            from . import rendering

            airline_code = context.xml_data['airline_iata_code']
            email_config = self.emailconf[airline_code]

            message = EmailMessage()
            for key, value in email_config.items():
                if key != 'template':
                    message[key] = value.format(**context.xml_data)

            plaintext = rendering.render(email_config['template'], context.xml_data)
            html = f'<pre>{plaintext}</pre>'
            message.set_content(plaintext)
            message.add_alternative(html, subtype='html')

            with smtplib.SMTP(**self.smtpconf) as smtp:
                smtp.send_message(message)
                logger.info(f"Email sent: {message['subject']} to {message['to']}")

            return True
        except Exception as e:
            logger.exception('Failed to send email')
            context.errors.append(e)
            return True  # Continue even if email fails


class PrintOutput(Stage):

    def process(self, context):
        print(context.as_dict())
        return True


class AirlineEmailOutput(Stage):
    """
    Write output file from rendered template.
    """

    def __init__(self, smtpconf, mapping):
        self.smtpconf = smtpconf
        self.mapping = mapping

    def process(self, context):
        """
        """
        import os
        import smtplib
        from email.message import EmailMessage
        from . import rendering

        airline_code = context.xml_data['airline_iata_code']
        email_config = self.mapping.get(airline_code)

        template = email_config['template']

        contents = rendering.render(template, context.xml_data)

        message = EmailMessage()
        for key, value in email_config.items():
            if key != 'template':
                message[key] = value.format(**context.xml_data)

        plaintext = rendering.render(email_config['template'], context.xml_data)
        html = f'<pre>{plaintext}</pre>'
        message.set_content(plaintext)
        message.add_alternative(html, subtype='html')

        with smtplib.SMTP(**self.smtpconf) as smtp:
            smtp.send_message(message)
            logger.info(f"Email sent: {message['subject']} to {message['to']}")

        return True


class AirlineFileOutput(Stage):
    """
    Write output file from rendered template.
    """

    def __init__(self, mapping):
        self.mapping = mapping

    def process(self, context):
        """
        """
        import os
        from . import rendering

        airline_code = context.xml_data['airline_iata_code']
        file_config = self.mapping.get(airline_code)

        template = file_config['template']
        filename = file_config['filename'].format(**context.xml_data)

        contents = rendering.render(template, context.xml_data)

        filename = filename.format(**context.xml_data)
        filename = os.path.normpath(filename)

        logger.info('file: %s', filename)

        return True

        with open(filename, 'w') as output_file:
            output_file.write(contents)


class AirlineJSONOutput(Stage):
    """
    Write JSON output.
    """

    def __init__(self, filename, indent=2):
        self.filename = filename
        self.indent = indent

    def process(self, context):
        try:
            import os
            import json

            from datetime import date
            from datetime import datetime
            from datetime import time

            def json_serializer(obj):
                """
                Handle datetime objects.
                """
                if isinstance(obj, (datetime, date, time)):
                    return obj.isoformat()
                raise TypeError(f'Object of type {type(obj)} is not JSON serializable')

            airline_code = context.xml_data['airline_iata_code']
            output_path = self.filename.format(**context.xml_data)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            return True

            with output_path.open('w') as f:
                json.dump(context.xml_data, f, indent=self.indent, default=json_serializer)

            context.outputs_written.append(output_path)
            logger.info(f'JSON written: {output_path}')
            return True
        except Exception as e:
            logger.exception('Failed to write JSON')
            context.errors.append(e)
            return True


class FileMover(Stage):
    """
    Move processed file to archive.
    """

    def __init__(self, move_to: str):
        self.move_to = move_to

    def process(self, context):
        try:
            import shutil
            from .utils import path_format_data

            fmtdata = path_format_data(str(context.source_path))
            fmtdata.update(context.xml_data)
            dest_path = Path(self.move_to.format(**fmtdata))

            dest_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(context.source_path), str(dest_path))
            logger.info(f'Moved: {context.source_path.name} -> {dest_path}')
            return True
        except Exception as e:
            logger.exception('Failed to move file')
            context.errors.append(e)
            return True


class Pipeline:
    """
    Process files through a series of stages.
    """

    def __init__(self, stages, archive):
        self.stages = stages
        self.archive = archive

    def process_file(self, source_path, substitutions=None):
        """
        Process a single file through all stages.
        """
        from . import pluck

        context = ProcessingContext(
            source_path = source_path,
            xml_data = pluck.default_data(),
            archive = self.archive
        )

        logger.info(f'Processing: {source_path}')

        for stage in self.stages:
            stage_name = stage.__class__.__name__
            logger.debug(f'Stage: {stage_name}')

            should_continue = stage.process(context)

            if not should_continue:
                logger.warning(f'Stage {stage_name} aborted processing')
                break

        # Mark as processed
        self.archive.save(str(source_path))

        if context.errors:
            logger.warning(f'Completed with {len(context.errors)} errors')
        else:
            logger.info(f'Successfully processed: {source_path}')

        return context

    def run(self, sources, substitutions=None):
        """
        Run pipeline on all sources.
        """
        import datetime
        import os
        import time

        if substitutions is None:
            today = datetime.date.today()
            substitutions = {
                'today': today,
                'yesterday': today - datetime.timedelta(days=1),
                'tomorrow': today + datetime.timedelta(days=1),
            }

        for path in sources:
            logger.info('path: %r', path)

            # Skip if already processed
            if self.archive.check(path):
                logger.debug(f'Already processed: {path}')
                continue

            # Skip empty files
            if os.stat(path).st_size == 0:
                logger.info(f'Skipping empty file: {path}')
                continue

            self.process_file(path, substitutions)

import logging

from marshmallow.exceptions import MarshmallowError

from extradata import ExtradataError
from lido import LIDOWeightBalanceMessage

from .exceptions import ExtractError

logger = logging.getLogger(__name__)

def log_marshmallow_error(marshmallow_error, logfunc):
    # Prettier line-based output for marshmallow.ValidationError
    # exceptions, with the data that failed.
    # Print the original in case the prettier output loses something.
    # key, [<validation error>, ...]
    for key, error_messages in marshmallow_error.messages.items():
        for errmsg in error_messages:
            logfunc(errmsg)

class Runner:
    """
    Lido weight and balance configuration runner.
    """

    # format for how messages get logged, nothing to do with processing or extracting.
    message_fmt = '{0.date:%Y-%m-%d %H:%M:%S} {0.subject!r}'.format

    def __init__(self, message_fmt=None):
        self.message_fmt = message_fmt or self.message_fmt

    def process_aircraft_registration_airline_mapping(self, mapping):
        # optional config overrides aircraft registration to airline mapping
        # this way, in configuration, one can hit a database for current data
        # instead of relying on a file or some such.
        import extradata
        extradata.aircraftregistration = mapping
        logger.debug(
            'extradata.aircraftregistration configured with %s', mapping)

    def process_message(
        self,
        message,
        message_processor,
        schema,
        message_class,
        output,
        message_archive,
        raise_exc,
    ):
        logger.debug('processing message ' + self.message_fmt(message))
        # return values
        extract_data = None
        loadplan = None
        lido_message = None
        path = None
        errors = dict(
            marshmallow_error = None,
            extract_error = None,
        )
        try:
            extract_data = message_processor(message)
        except ExtractError as e:
            if raise_exc:
                raise
            logger.exception(e)
        else:
            logger.debug('extract_data: %s', extract_data)
            try:
                loadplan = schema.load(extract_data)
            except MarshmallowError as marshmallow_error:
                if raise_exc:
                    raise
                errors['marshmallow_error'] = marshmallow_error
                logger.exception(marshmallow_error)
                log_marshmallow_error(marshmallow_error, logger.error)
            except ExtradataError as extract_error:
                if raise_exc:
                    raise
                logger.exception('An exception occurred')
                errors['extract_error'] = extract_error
            else:
                logger.debug('loadplan loaded from schema')
                lido_message = message_class(loadplan)
                logger.debug('lido_message created')
                path = output.write(lido_message)
                logger.debug('%s', path)
                message_archive.save(message)
                logger.info('message processed and archived ' + self.message_fmt(message))
        rv = dict(
            message = message,
            extract_data = extract_data,
            loadplan = loadplan,
            lido_message = lido_message,
            output = output,
            path = path,
            **errors,
        )
        return rv

    def from_config(self, config, raise_exc):
        """
        Normal run as configured from Python file.
        """
        airline_mapping = config.get('AIRCRAFT_REGISTRATION_AIRLINE_MAPPING')
        source = config['SOURCE']
        schema_class = config['SCHEMA_CLASS']
        message_filter = config['MESSAGE_FILTER']
        message_processor = config['MESSAGE_PROCESSOR']
        output = config['OUTPUT']
        message_archive = config['MESSAGE_ARCHIVE']
        message_class = config.get('MESSAGE_CLASS', LIDOWeightBalanceMessage)
        raise_exc = config.get('RAISE_EXC', raise_exc)
        rv = self.run(
            source,
            schema_class,
            message_filter,
            message_processor,
            output,
            message_archive,
            message_class,
            raise_exc,
            airline_mapping = airline_mapping,
        )
        return rv

    def run_stepped(
        self,
        source,
        schema_class,
        message_filter,
        message_processor,
        output,
        message_archive,
        message_class,
        raise_exc,
        airline_mapping = None,
    ):
        """
        Run in steps with explicitly passed values for use in apps that want this control.
        """
        if airline_mapping:
            self.process_aircraft_registration_airline_mapping(config)
        schema = schema_class()
        for message in source.itermessages():
            if not message_filter.filter(message):
                continue
            step_result = self.process_message(
                message,
                message_processor,
                schema,
                message_class,
                output,
                message_archive,
                raise_exc
            )
            yield step_result

    def run(
        self,
        source,
        schema_class,
        message_filter,
        message_processor,
        output,
        message_archive,
        message_class,
        raise_exc,
        airline_mapping = None,
    ):
        """
        Full run return list of results with explicitly passed in objects.
        """
        generator = self.run_stepped(
            source,
            schema_class,
            message_filter,
            message_processor,
            output,
            message_archive,
            message_class,
            raise_exc
        )
        results = []
        for step_result in generator:
            results.append(step_result)
        return results

    def __call__(self, config, raise_exc=False):
        """
        A single run--download, filter, process and write (file) for the LIDO
        messaging system to consume.
        """
        # __call__ should remain like the `def run` func was.
        # TODO: pushing airline mapping config down into one function
        return self.from_config(config, raise_exc)

run = Runner()

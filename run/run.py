import logging

from marshmallow.exceptions import MarshmallowError

from extradata import ExtradataError
from lido import LIDOWeightBalanceMessage

from .exceptions import ExtractError

def run(config, raise_exc=False):
    """
    A single run--download, filter, process and write (file) for the LIDO
    messaging system to consume.
    """
    logger = logging.getLogger(__name__)

    # optional config overrides aircraft registration to airline mapping
    # this way, in configuration, one can hit a database for current data
    # instead of relying on a file or some such.
    if 'AIRCRAFT_REGISTRATION_AIRLINE_MAPPING' in config:
        import extradata
        extradata.aircraftregistration = config['AIRCRAFT_REGISTRATION_AIRLINE_MAPPING']

    source = config['SOURCE']
    schema_class = config['SCHEMA_CLASS']
    message_filter = config['MESSAGE_FILTER']
    message_processor = config['MESSAGE_PROCESSOR']
    output = config['OUTPUT']
    message_archive = config['MESSAGE_ARCHIVE']
    message_class = config.get('MESSAGE_CLASS', LIDOWeightBalanceMessage)
    raise_exc = config.get('RAISE_EXC', raise_exc)

    # format for how messages get logged, nothing to do with processing or extracting.
    message_fmt = '{0.date:%Y-%m-%d %H:%M:%S} {0.subject!r}'.format

    schema = schema_class()
    for message in source.itermessages():
        if not message_filter.filter(message):
            logger.debug(
                'message filter rejected ' + message_fmt(message))
            continue
        logger.debug('processing message ' + message_fmt(message))
        try:
            extract_data = message_processor(message)
        except ExtractError as e:
            if raise_exc:
                raise
            logger.exception(e)
        else:
            try:
                loadplan = schema.load(extract_data)
            except MarshmallowError as error:
                if raise_exc:
                    raise
                # Prettier line-based output for marshmallow.ValidationError
                # exceptions, with the data that failed.
                # Print the original in case the prettier output loses something.
                logger.exception(error)
                # key, [<validation error>, ...]
                for key, error_messages in error.messages.items():
                    if extract_data is not None:
                        if key in extract_data:
                            for errmsg in error_messages:
                                logger.error(f'{key} {errmsg} ({extract_data[key]!r})')
                    else:
                        for errmsg in error_messages:
                            logger.error(errmsg)
            except ExtradataError:
                if raise_exc:
                    raise
                logger.exception('An exception occurred')
            else:
                logger.debug('loadplan loaded from schema')
                lido_message = message_class(loadplan)
                logger.debug('lido_message created')
                path = output.write(lido_message)
                logger.debug(str(path))
                message_archive.save(message)
                logger.info('message processed and archived ' + message_fmt(message))

import logging

from marshmallow import ValidationError

from lido import LIDOWeightBalanceMessage

def run(config):
    logger = logging.getLogger(__name__)

    # optional config overrides aircraft registration to airline mapping
    if 'AIRCRAFT_REGISTRATION_AIRLINE_MAPPING' in config:
        import extradata
        extradata.aircraftregistration = config['AIRCRAFT_REGISTRATION_AIRLINE_MAPPING']

    source = config['SOURCE']
    schema_class = config['SCHEMA_CLASS']
    message_filter = config['MESSAGE_FILTER']
    message_processor = config['MESSAGE_PROCESSOR']
    output = config['OUTPUT']
    message_archive = config['MESSAGE_ARCHIVE']

    message_fmt = '{0.date:%Y-%m-%d %H:%M:%S} {0.text!r}'.format

    schema = schema_class()
    for message in source.itermessages():
        if not message_filter.filter(message):
            logger.info(
                'message filter rejected ' + message_fmt(message))
            continue
        logger.info('processing message ' + message_fmt(message))
        try:
            message_data = message_processor(message)
        except Exception as e:
            logger.exception(e)
        else:
            try:
                loadplan = schema.load(message_data)
            except ValidationError as error:
                logger.exception(error)
                for key, messages in error.messages.items():
                    if not key.startswith('_'):
                        for message in messages:
                            logger.error(f'{key} {message} ({message_data[key]!r})')
            except Exception as e:
                logger.exception(e)
            else:
                logger.info('loadplan loaded from schema')
                lido_message = LIDOWeightBalanceMessage(loadplan)
                logger.info('lido_message created')
                output.write(lido_message)
                message_archive.save(message)
                logger.info('message archived')
        break

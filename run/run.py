import logging

from marshmallow import ValidationError

from lido import LIDOWeightBalanceMessage

def run(conf):
    logger = logging.getLogger(__name__)

    source = conf['SOURCE']
    schema_class = conf['SCHEMA_CLASS']
    message_filter = conf['MESSAGE_FILTER']
    message_processor = conf['MESSAGE_PROCESSOR']
    output = conf['OUTPUT']
    message_archive = conf['MESSAGE_ARCHIVE']

    schema = schema_class()
    for message in source.itermessages():
        if not message_filter.filter(message):
            logger.info('message filter rejected %r', message)
            continue
        logger.info('message %r', message)
        try:
            message_data = message_processor(message)
        except Exception as e:
            logger.exception(e)
        else:
            logger.info('message_data %r', message_data)
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
                logger.info('loadplan %r', loadplan)
                lido_message = LIDOWeightBalanceMessage(loadplan)
                logger.info('lido_message %r', lido_message)
                output.write(lido_message)
                message_archive.save(message)
                logger.info('saved %r', message)

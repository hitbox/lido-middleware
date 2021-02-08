import logging

from marshmallow import ValidationError

from lido import LIDOWeightBalanceMessage

def run(conf):
    logger = logging.getLogger(__name__)

    source = conf['SOURCE']
    schema_class = conf['SCHEMA_CLASS']
    message_processor = conf['MESSAGE_PROCESSOR']
    output = conf['OUTPUT']

    schema = schema_class()
    for msg in source.itermessages():
        try:
            message_data = message_processor(msg)
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
                lido_message = LIDOWeightBalanceMessage(loadplan)
                output.write(lido_message)

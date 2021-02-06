import ftplib
import io
import logging

from datetime import date
from datetime import timedelta
from pprint import pformat

from marshmallow import ValidationError
from imap_tools import AND
from imap_tools import MailBox

from lido import LIDOWeightBalanceMessage

from utils import _resolve
from utils import cleanlines
from utils import hide

def run(conf):
    logger = logging.getLogger(__name__)
    schema = conf.schema_class()

    for msg in conf.source.itermessages():
        message_data = conf.message_processor(msg)
        try:
            loadplan = schema.load(message_data)
        except ValidationError as error:
            logger.exception(error)
            for key, messages in error.messages.items():
                for message in messages:
                    logger.error(f'{key} {message} ({message_data[key]!r})')
        else:
            lido_message = LIDOWeightBalanceMessage(loadplan)
            lido_string = str(lido_message)
            logger.info(lido_string)


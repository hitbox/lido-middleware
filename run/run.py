import ftplib
import io
import logging

from datetime import date
from datetime import timedelta
from pprint import pformat

from imap_tools import AND
from imap_tools import MailBox

from lido import LIDOWeightBalanceMessage

from utils import cleanlines
from utils import hide

def run(emailconf, message_processor, schema, ftpconf):
    """
    Download recent emails, convert them to LIDO weight and balance message
    strings and upload to ftp.

    :param emailconf: email account info and message fetching config.
    :param message_processor: callable to take email message and return loadplan data.
    :param schema: instance of a schema to convert result of message_processor.
    :param ftpconf: ftp account info and output path format string.
    """
    logger = logging.getLogger(__name__)
    logger.info('starting')

    mailhost = emailconf['host']
    mailusername = emailconf['username']
    mailpassword = emailconf['password']
    msglimit = emailconf.get('limit')
    if msglimit is not None:
        msglimit = int(msglimit)

    # criteria for messages since yesterday, from the pstl message sender
    # XXX: this will probably have to be configurable and something more like:
    #      "since last run"
    from_ = emailconf['from_']
    since_yesterday_from = AND(
        from_ = from_,
        date_gte = date.today() - timedelta(days=1), # yesterday
    )

    ftphost = ftpconf['host']
    ftpusername = ftpconf['username']
    ftppassword = ftpconf['password']
    pathfmt = ftpconf['pathfmt']

    logger.debug('mail host: %s', mailhost)
    logger.debug('mail username: %s', mailusername)
    logger.debug('mail password: %s', hide(mailpassword))
    logger.debug('mail fetch limit: %s', msglimit)
    logger.debug('mail fetch criteria: %s', since_yesterday_from)

    logger.debug('ftp host: %s', ftphost)
    logger.debug('ftp username: %s', ftpusername)
    logger.debug('ftp password: %s', hide(ftppassword))
    logger.debug('message_processor: %r', message_processor)
    logger.debug('schema: %r', schema)
    logger.debug('pathfmt: %r', pathfmt)

    logger.info('logging into email and ftp')
    with MailBox(mailhost).login(mailusername, mailpassword) as mailbox, \
            ftplib.FTP(ftphost, ftpusername, ftppassword) as ftp:
        logger.info('fetching messages')
        messages = mailbox.fetch(
            since_yesterday_from,
            limit = msglimit,
            mark_seen = False
        )
        for message in messages:
            logger.info('message subject: %s', message.subject)
            logger.debug('message text:\n%s', cleanlines(message.text))
            if not message.attachments:
                logger.debug('no attachments')
            else:
                for num, attachment in enumerate(message.attachments, start=1):
                    logger.debug('message attachment %s %r',
                                 num, attachment.filename)
            logger.info('processing message')
            loadplan_data = message_processor(message)
            logger.debug('loadplan_data:\n%s', pformat(loadplan_data))
            logger.info('loading schema')
            loadplan = schema.load(loadplan_data)
            logger.debug('loadplan:\n%s', pformat(loadplan))
            lidomsg = LIDOWeightBalanceMessage(loadplan)
            lidomsg_text = str(lidomsg)
            logger.debug('lido message text %r', lidomsg_text)
            output_fp = io.BytesIO(lidomsg_text.encode('utf8'))
            path = pathfmt.format(lidomsg=lidomsg)
            logger.info('uploading file to ftp: %r', path)
            ftp.storbinary('STOR ' + path, output_fp)
            logger.info('run done')

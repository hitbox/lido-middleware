import datetime
import sys
import types

from abc import abstractmethod

from utils import _resolve

class Source:
    """
    Produce messages from something.
    """

    @abstractmethod
    def itermessages(self):
        """
        Should generate iterable of load plan messages to extract from.
        """
        raise NotImplementedError


class Output:
    """
    Writes LIDO message to something.
    """

    @abstractmethod
    def write(self, lido_message):
        raise NotImplementedError


class MessageFilter:
    """
    Decide if email message should be processed.
    """

    @abstractmethod
    def filter(self, message):
        raise NotImplementedError


class MessageArchive:
    """
    Save a message so that it can be ignored next run.
    """

    @abstractmethod
    def save(self, message):
        raise NotImplementedError


class FakeMessage:

    def __init__(self, subject, date, text):
        self.subject = subject
        self.date = date
        self.text = text


class GlobSource(Source):

    def __init__(self, pathname):
        self.pathname = pathname

    def iterfilenames(self):
        from glob import glob
        for fn in glob(self.pathname):
            yield fn

    def itermessages(self):
        import datetime
        import os
        for fn in self.iterfilenames():
            with open(fn) as fp:
                stat = os.stat(fn)
                date = datetime.datetime.fromtimestamp(stat.st_mtime)
                fakemsg = FakeMessage(fn, date, fp.read())
                yield fakemsg


class PickleGlobSource(GlobSource):

    def itermessages(self):
        import pickle
        for fn in self.iterfilenames():
            with open(fn, 'rb') as fp:
                messages = pickle.load(fp)
                if not isinstance(messages, (list, tuple, set)):
                    messages = [messages]
                for message in messages:
                    message._filename = fn
                    yield message


class MailBoxSource(Source):
    """
    Loadplan messages from email mailbox.
    """

    def __init__(self, host, username, password,
            fetch_criteria=None,
            fetch_limit=None,
            reverse = True,
        ):
        self.host = host
        self.username = username
        self.password = password
        self.fetch_criteria = fetch_criteria
        self.fetch_limit = fetch_limit
        self.reverse = reverse

    def itermessages(self):
        from imap_tools import MailBox
        with MailBox(self.host) as mailbox:
            mailbox.login(self.username, self.password)
            messages = mailbox.fetch(
                    self.fetch_criteria,
                    limit = self.fetch_limit,
                    mark_seen = False,
                    reverse = self.reverse)
            yield from messages


class MultipleMailBoxSource(Source):
    """
    Loadplan messages from multiple mailboxes.
    """

    def __init__(self, sources):
        """
        :param sources: container of MailBoxSource objects
        """
        self.sources = sources

    def itermessages(self):
        for source in self.sources:
            yield from source.itermessages()


class PassMessageFilter(MessageFilter):
    """
    Always true message filter.
    """

    def __init__(self, archive):
        pass

    def filter(self, message):
        """
        Return True to process message. This always returns True.
        """
        return True


class SHA1HexArchiveFilter(MessageFilter):
    """
    Filter out SHA1 hex digests that exist in a file.
    """

    def __init__(self, path):
        self.path = path

    def filter(self, hexdigest):
        from pathlib import Path
        if not Path(self.path).exists():
            return True
        with open(self.path) as archive_file:
            saved = archive_file.read().splitlines()
            return hexdigest not in saved


class ArchiveMessageFilter(MessageFilter):

    def __init__(self, archive, subject=None):
        self.archive = archive
        self.subject = subject

    def filter(self, message):
        """
        Returns True if message does not exist in archive.
        """
        import hashlib

        from pathlib import Path

        subject = self.subject
        if subject is None:
            subject = lambda s: True

        path = Path(self.archive)
        if not path.exists():
            return True
        else:
            with open(self.archive) as archive_file:
                archived = set(line.strip() for line in archive_file.readlines())
                sha1 = hashlib.sha1(bytes(message.obj))
                not_in_archive = sha1.hexdigest() not in archived
                return not_in_archive and subject(message.subject)


class StreamOutput(Output):

    def __init__(self, stream=None):
        if stream is None:
            stream = sys.stderr
        self.stream = stream

    def write(self, lido_message):
        self.stream.write(str(lido_message))


class NullOutput(Output):

    def write(self, lido_message):
        pass


class FileOutput(Output):
    """
    Write LIDO message string to file.
    """

    def __init__(self, pathfmt, mode='w', preprocessor=str):
        """
        :param pathfmt: format string, lidomsg=LIDOWeightBalanceMessage instance.
        """
        self.pathfmt = pathfmt
        self.mode = mode
        self.preprocessor = preprocessor

    def write(self, lido_message):
        context = dict(
            lidomsg = lido_message,
            now = datetime.datetime.now(),
        )
        path = self.pathfmt.format(**context)
        with open(path, self.mode) as fp:
            fp.write(self.preprocessor(lido_message))
        return path


class PassMessageArchive(MessageArchive):
    """
    Empty do-nothing archiver to meet spec.
    """

    def __init__(self, archive):
        pass

    def save(self, message):
        pass


class FileSystemArchive(MessageArchive):

    def __init__(self, path):
        self.path = path

    def write(self, payload):
        with open(self.path, 'a') as archive_file:
            archive_file.write(payload)


class SHA1FakeMessageArchive(FileSystemArchive):

    def save(self, message):
        import hashlib
        sha1 = haslib.sha1(message.text.encode('utf8'))
        payload = sha1.hexdigest() + '\n'
        self.write(payload)


class SHA1MessageArchive(FileSystemArchive):
    """
    Archive an email message as SHA1 in a file.
    """

    def save(self, message):
        """
        Save the SHA1 hashed bytes of email message to line-based file.
        :param message: imap_tools.message.MailMessage object.
        """
        import hashlib
        sha1 = hashlib.sha1(bytes(message.obj))
        payload = sha1.hexdigest() + '\n'
        self.write(payload)


class RunConfig:

    def __init__(self, source, message_processor, schema_class, output):
        self.source = source
        self.message_processor = message_processor
        self.schema_class = schema_class
        self.output = output


def file_config(config_processor_or_file, defaults=None):
    import configparser

    if isinstance(config_processor_or_file, configparser.RawConfigParser):
        cp = config_processor_or_file
    else:
        cp = configparser.ConfigParser(defaults)
        fn = config_processor_or_file
        if hasattr(fn, 'readline'):
            cp.read_file(fn)
        else:
            cp.read(fn)

    run_section = cp['run']

    # source
    source_section = cp['source_' + run_section['source']]
    source_class = _resolve(source_section['class'])
    source_args = eval(source_section['args'])
    source_kwargs = source_section.get('kwargs', {})
    source = source_class(*source_args, **source_kwargs)

    # filter
    message_filter = run_section['message_filter']
    if message_filter != 'None':
        message_filter_section = cp['message_filter_' + message_filter_]
        raise NotImplementedError

    message_processor = _resolve(run_section['message_processor'])
    schema_class = _resolve(run_section['schema_class'])
    output_section = cp['output_' + run_section['output']]
    output_class = _resolve(output_section['class'])
    output_args = eval(output_section['args'])
    output = output_class(*output_args)

    runconfig = RunConfig(
        source = source,
        message_processor = message_processor,
        schema_class = schema_class,
        output = output,
    )

    return runconfig

def pyfile_config(path):
    """
    Return dict config from python file.

    :param path: path to python file.
    """
    d = types.ModuleType("config")
    d.__file__ = path
    with open(path, mode="rb") as config_file:
        exec(compile(config_file.read(), path, "exec"), d.__dict__)

    config = {}
    for key in dir(d):
        if key.isupper():
            config[key] = getattr(d, key)

    return config

from utils import _resolve

class Output:

    def write(self, lido_message):
        raise NotImplementedError


class FileOutput(Output):

    def __init__(self, pathfmt, mode='w'):
        self.pathfmt = pathfmt
        self.mode = mode

    def write(self, lido_message):
        context = dict(lidomsg=lido_message)
        path = self.pathfmt.format(**context)
        with open(path, self.mode) as fp:
            fp.write(str(lido_message))


class Source:

    def itermessage(self):
        raise NotImplementedError


class PickleSource(Source):

    def __init__(self, *filenames):
        self.filenames = filenames

    def itermessages(self):
        import pickle
        for fn in self.filenames:
            with open(fn, 'rb') as fp:
                message = pickle.load(fp)
                yield message


class MailBoxSource(Source):

    def __init__(self, host, username, password, fetch_criteria=None):
        pass


class MailConfig:

    def __init__(self, host, username, password, fetch_config):
        self.host = host
        self.username = username
        self.password = password
        self.fetch_config = fetch_config


class FetchConfig:

    def __init__(self, limit, mark_seen=None):
        """
        Arguments for MailBox.fetch
        :param limit: number of messages to fetch
        :param mark_seen: mark messages as seen. this changes MailBox.fetch to
                          default False.
        """
        self.limit = limit
        if mark_seen is None:
            mark_seen = False
        self.mark_seen = mark_seen


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

    source_section = cp['source_' + run_section['source']]

    source_class = _resolve(source_section['class'])
    source_args = eval(source_section['args'])
    source = source_class(*source_args)

    #mailconfig = MailConfig(
    #    source_section['host'],
    #    source_section['username'],
    #    source_section['password'],
    #    FetchConfig(
    #        source_section['fetch_limit'],
    #        source_section.get('mark_seen')
    #    )
    #)
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

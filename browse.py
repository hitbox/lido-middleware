import argparse
import code
import configparser
import logging

import run.config

def main(argv=None):
    """
    Browse the processed data in mailbox pickles with an interactive
    interpreter.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog='browse')
    parser.add_argument('config', nargs='+')
    args = parser.parse_args(argv)

    logging.basicConfig()
    logger = logging.getLogger()

    cp = configparser.ConfigParser()
    cp.read(args.config)

    conf = run.config.file_config(cp)

    alldata = []
    messages = []
    extracts = []
    loadplans = []
    schema = conf.schema_class()
    for msg in conf.source.itermessages():
        messages.append(msg)
        item = dict(msg=msg, message_data=None, loadplan=None)
        alldata.append(item)
        try:
            message_data = conf.message_processor(msg)
        except Exception as e:
            logger.exception(e)
        else:
            extracts.append(message_data)
            item['message_data'] = message_data
            try:
                loadplan = schema.load(message_data)
            except Exception as e:
                logger.exception(e)
            else:
                loadplans.append(loadplan)
                item['loadplan'] = loadplan

    context = dict(
        alldata = alldata,
        messages = messages,
        extracts = extracts,
        loadplans = loadplans,
    )
    code.interact(local=context)

if __name__ == '__main__':
    main()

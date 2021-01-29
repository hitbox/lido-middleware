import argparse
import code
import configparser

from pathlib import Path

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    # TODO: config from env var
    parser.add_argument('config', type=Path)
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    dburi = cp['pstldata']['sqlalchemy_database_uri']

    engine = sa.create_engine(dburi)
    Session = sa.orm.sessionmaker()
    session = Session(bind=engine)

    context = globals()
    context.update(locals())
    code.interact(local=context)

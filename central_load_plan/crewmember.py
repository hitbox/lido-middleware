import argparse
import datetime
import configparser

import cx_Oracle as oracle
import sqlalchemy as sa

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('config', nargs='+')
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    url = sa.engine.url.URL.create(**cp['database'])
    engine = sa.create_engine(url, max_identifier_length=128)

    metadata = sa.MetaData()
    event_account = sa.Table('EVENT_ACCOUNT', metadata, autoload_with=engine)
    crew_member = sa.Table('CREW_MEMBER', metadata, autoload_with=engine)
    carrier_conversion = sa.Table('CARRIER_CONVERSION', metadata, autoload_with=engine)

    role_no_columns = [c for c in event_account.c if c.name.startswith('role_no_')]

    query = (
        sa.select(list(event_account.c))
        .where(sa.or_(*(c != 0 for c in role_no_columns)))
    )

    # different login based on airlineIATACode?
    # have observed 8C, ER, and GB in the XML

    # in the entire table only 0, 1002, and 1111 is used
    # i.e.: NONE, Voluntary, Reassign
    from pprint import pprint
    roles = set()
    for row in engine.execute(query):
        data = dict(zip((c.name for c in event_account.c), row))
        for c in role_no_columns:
            roles.add(data[c.name])
    pprint(roles)
    return

    query = (
        sa.select([
            sa.func.trim(crew_member.c.name).label('last_name'),
            sa.func.trim(crew_member.c.first_name),
            sa.func.trim(crew_member.c.employee_no),
        ])
        .join(event_account, event_account.c.tlc == crew_member.c.tlc)
        .where(
            event_account.c.day_of_origin.between(datetime.date(2021,4,1), datetime.date(2021,4,3))
        )
    )

    for row in engine.execute(query):
        print(row)

    # nothing in CARRIER_CONVERSION
    #print(list(engine.execute(sa.select(list(carrier_conversion.c)))))

    return

    import code
    code.interact(local=dict(**globals(), **locals()))

if __name__ == '__main__':
    main()

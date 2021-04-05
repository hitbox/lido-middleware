import argparse
import configparser
import datetime
import xml.etree.ElementTree as ET

from itertools import zip_longest

import cx_Oracle as oracle
import sqlalchemy as sa

from . import pluck
from . import schema

def fromdata(config, data):
    airline_code = data['airline_iata_code']
    airline_section = config[airline_code]
    url = sa.engine.url.URL.create(
        airline_section.get('drivername'),
        airline_section.get('username'),
        airline_section.get('password'),
        airline_section.get('host'),
        airline_section.get('port'),
        airline_section.get('database'),
    )
    engine = sa.create_engine(url, max_identifier_length=128)

    metadata = sa.MetaData()
    event_account = sa.Table('EVENT_ACCOUNT', metadata, autoload_with=engine)
    crew_member = sa.Table('CREW_MEMBER', metadata, autoload_with=engine)

    # NOTES:
    # * event_account does not really use the destination station, it seems to
    #   create a record for each leg using only the origin. So here, we just
    #   use the origin (dep_ap).
    query = (
        sa.select([
            sa.func.trim(crew_member.c.name), # last_name
            sa.func.trim(crew_member.c.first_name),
            sa.func.trim(crew_member.c.employee_no),
        ])
        .join(
            event_account,
            event_account.c.tlc == crew_member.c.tlc)
        .where(
            sa.and_(
                event_account.c.airline == data['airline_iata_code'],
                event_account.c.day_of_origin == data['leg_departure_date_utc'].date(),
                event_account.c.flight_no == data['flight_number'],
                event_account.c.dep_ap == data['origin_iata'],
            )
        )
    )
    # NOTES:
    # seat: PIC, SIC
    # PIC: Pilot in Command
    keys = ['last_name', 'first_name', 'employee_number', 'seat']
    crewmembers = [dict(zip_longest(keys, row)) for row in engine.execute(query)]
    return crewmembers

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('config', nargs='+')
    parser.add_argument('xmlfile')
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    tree = ET.parse(args.xmlfile)
    root = tree.getroot()
    data = pluck.fromxml(root)
    data = schema.OperationalFlightPlanSchema().load(data)

    crewmembers = fromdata(cp, data)
    for row in crewmembers:
        print(row)

if __name__ == '__main__':
    main()

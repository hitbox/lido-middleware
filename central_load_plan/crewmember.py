import argparse
import configparser
import datetime
import os
import textwrap
import xml.etree.ElementTree as ET

from itertools import zip_longest
from pathlib import Path

import cx_Oracle as oracle
import sqlalchemy as sa

from . import pluck
from . import schema

class CrewMemberResult:
    """
    Simple structure holding crewmembers and metadata so that the web app can
    display useful info.
    """

    def __init__(self, crewmembers, query, data, engine):
        self.crewmembers = crewmembers
        self.query = query
        self.data = data
        self.engine = engine

    def __bool__(self):
        return bool(self.crewmembers)


def jumpseat_type_and_remaining(substring_between_bars):
    """
    Parse substrings in remark for type of seat and the remaining text.
    """
    return (substring_between_bars[0], substring_between_bars[1:])

JUMPSEAT_KEYS = ('last_name', 'first_name', 'employee_number', 'seat', 'seat_order')

def parse_for_other(string):
    """
    Parse jump seats for type O(ther).
    """
    person_dict = dict(zip(JUMPSEAT_KEYS, string.split(';'), strict=True))
    return person_dict

def fromdata(dbconfig, data):
    """
    Return airline specific, object containing crewmembers in list.
    """
    airline_code = data['airline_iata_code']
    airline_dbconfig = dbconfig[airline_code]
    if 'oracle_lib_dir' in airline_dbconfig:
        oracle_lib_dir = airline_dbconfig['oracle_lib_dir']
        try:
            oracle.init_oracle_client(lib_dir=oracle_lib_dir)
        except oracle.ProgrammingError:
            # already initialized
            pass

    # connect
    keys = ['username', 'password', 'host', 'port', 'database', 'query']
    connconf = {key: val for key,val in airline_dbconfig.items() if key in keys}
    url = sa.engine.url.URL.create(airline_dbconfig['drivername'], **connconf)
    engine = sa.create_engine(url, max_identifier_length=128)

    # tables
    metadata = sa.MetaData()
    chain_item_daily = sa.Table('chain_item_daily', metadata, autoload_with=engine)
    crew_member = sa.Table('crew_member', metadata, autoload_with=engine)
    non_crew_member = sa.Table('non_crew_member', metadata, autoload_with=engine)
    duty = sa.Table('duty', metadata, autoload_with=engine)
    item_daily = sa.Table('item_daily', metadata, autoload_with=engine)
    remark_of_event = sa.Table('remark_of_event', metadata, autoload_with=engine)

    # build query
    query_crew = (
        sa.select([
            sa.func.trim(crew_member.c.name).label('last_name'),
            sa.func.trim(crew_member.c.first_name).label('first_name'),
            sa.func.trim(crew_member.c.employee_no).label('employee_number'),
            sa.case(
                (sa.and_(item_daily.c.type == 'L', duty.c.assigned_rank == 0), 'PIC'),
                (sa.and_(item_daily.c.type == 'L', duty.c.assigned_rank == 1), 'SIC'),
                (sa.and_(item_daily.c.type == 'L', duty.c.assigned_rank == 2), 'IRO'),
                (sa.and_(item_daily.c.type == 'L', duty.c.assigned_rank == 3), 'CP'),
                (sa.and_(item_daily.c.type == 'L', duty.c.assigned_rank == 5), 'FA'),
                (item_daily.c.type == 'F', 'ACM'),
            ).label('seat'),
            sa.case(
                (item_daily.c.type == 'L', duty.c.assigned_rank),
                (item_daily.c.type == 'F', 99),
            ).label('seat_order'),
        ])
        .select_from(item_daily)
        .join(
            chain_item_daily,
            chain_item_daily.c.item_daily_uno == item_daily.c.uno
        ).join(
            duty,
            duty.c.chain_daily_uno == chain_item_daily.c.chain_daily_uno
        ).join(
            crew_member,
            crew_member.c.tlc == duty.c.tlc
        ).where(
            sa.and_(
                item_daily.c.airline == data['airline_iata_code'],
                item_daily.c.day_of_origin == data['flight_origin_date'],
                item_daily.c.flight_no == data['flight_number'],
                item_daily.c.airport_c_is_dep == data['origin_iata'],
                item_daily.c.departure_date_scd == data['scheduled_departure_time'].date(),
                # departure_time_scd is stored as CHAR(4)
                item_daily.c.departure_time_scd == data['scheduled_departure_time'].strftime('%H%M'),
            )
        ).order_by('seat_order')
    )

    query_jumpseats = (
        sa.select([
            remark_of_event.c.remark,
        ]).select_from(
            item_daily
        ).join(
            remark_of_event,
            remark_of_event.c.uno == item_daily.c.uno
        ).where(
            sa.and_(
                item_daily.c.airline == data['airline_iata_code'],
                item_daily.c.day_of_origin == data['flight_origin_date'],
                item_daily.c.flight_no == data['flight_number'],
                item_daily.c.airport_c_is_dep == data['origin_iata'],
                item_daily.c.departure_date_scd == data['scheduled_departure_time'].date(),
                # departure_time_scd is stored as CHAR(4)
                item_daily.c.departure_time_scd == data['scheduled_departure_time'].strftime('%H%M'),
                # is jumpseat remark
                remark_of_event.c.type == 'J',
            )
        ))

    # run query and return result
    person_tables = {
        # (table, field for person id)
        'C': (crew_member, crew_member.c.employee_no),
        'N': (non_crew_member, non_crew_member.c.employee_id),
    }
    with engine.connect() as conn:
        # add crew members first
        crewmembers = list(map(dict, conn.execute(query_crew)))
        # add jump seat people substrings
        jumpseats = [
            jumpseat_type_and_remaining(jumpseat_str)
            for result in conn.execute(query_jumpseats)
            for jumpseat_str in result.remark.split('|')
        ]
        # parse substring further for other type or lookup from database for
        # crew and employees with identification.
        for person_type, remaining in jumpseats:
            if person_type not in person_tables:
                # person_id_or_string is just a string
                person_string = remaining
                person = parse_for_other(person_string)
                crewmembers.append(person)
            else:
                # lookup from database
                person_id = remaining
                table, field = person_tables[person_type]
                query = sa.select([
                        sa.func.trim(table.c.name).label(JUMPSEAT_KEYS[0]), # last_name
                        sa.func.trim(table.c.first_name).label(JUMPSEAT_KEYS[1]), # first_name
                        sa.func.trim(field).label(JUMPSEAT_KEYS[2]), # employee_number
                        sa.literal_column("'ACM'", type_=sa.String()).label(JUMPSEAT_KEYS[3]), # seat
                        sa.literal_column('999', type_=sa.Integer()).label(JUMPSEAT_KEYS[4]), # seat_order
                    ]).where(
                        field == person_id
                    )
                for jumpseat in conn.execute(query):
                    crewmembers.append(jumpseat)

        result = CrewMemberResult(crewmembers, query_crew, data, engine)
        return result

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('xmlfiles', nargs='+')
    parser.add_argument('--config', nargs='+')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--report', action='store_true')
    group.add_argument('--report-file', action='store_true')
    args = parser.parse_args(argv)

    filenames = []
    if args.config:
        filenames.extend(args.config)
    if 'CREWMEMBER_CONFIG' in os.environ:
        filenames.append(os.environ['CREWMEMBER_CONFIG'])
    cp = configparser.ConfigParser()
    cp.read(filenames)

    for fn in args.xmlfiles:
        tree = ET.parse(fn)
        root = tree.getroot()
        data = pluck.fromxml(root)
        data = schema.OperationalFlightPlanSchema().load(data)
        result = fromdata(cp, data)
        if args.report:
            if result:
                print(fn + ' ' + result.engine.url.render_as_string())
        elif args.report_file:
            # same name, current dir
            output = Path(fn).name
            with open(output, 'w') as fp:
                print(fn, file=fp)
                for row in result.crewmembers:
                    print(row, file=fp)
                print(file=fp)
                print(result.engine.url.render_as_string(), file=fp)
                sql = result.query.compile(result.engine, compile_kwargs={'literal_binds': True})
                sql = textwrap.wrap(sql)
                sql = '\n'.join(sql)
                print(sql, file=fp)
        else:
            print(fn)
            for row in result.crewmembers:
                print(row)

if __name__ == '__main__':
    main()

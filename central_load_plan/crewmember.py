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

    def __init__(self, crewmembers, query, data, engine):
        self.crewmembers = crewmembers
        self.query = query
        self.data = data
        self.engine = engine

    def __bool__(self):
        return bool(self.crewmembers)


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

    chain_item_daily = sa.Table('chain_item_daily', metadata, autoload_with=engine)
    crew_member = sa.Table('crew_member', metadata, autoload_with=engine)
    duty = sa.Table('duty', metadata, autoload_with=engine)
    item_daily = sa.Table('item_daily', metadata, autoload_with=engine)

    query = (sa.select([
            sa.func.trim(crew_member.c.name).label('last_name'),
            sa.func.trim(crew_member.c.first_name).label('first_name'),
            crew_member.c.employee_no,
            sa.case(
                sa.and_(item_daily.c.type == 'L', duty.c.assigned_rank == 0), 'PIC'),
                sa.and_(item_daily.c.type == 'L', duty.c.assigned_rank == 1), 'SIC'),
                sa.and_(item_daily.c.type == 'L', duty.c.assigned_rank == 2), 'IRO'),
                sa.and_(item_daily.c.type == 'L', duty.c.assigned_rank == 3), 'CP'),
                sa.and_(item_daily.c.type == 'L', duty.c.assigned_rank == 5), 'FA'),
                (item_daily.c.type == 'F', 'ACM'),
            ).label('seat')
        ])
        .select_from(item_daily)
        .join(chain_item_daily, chain_item_daily.c.item_daily_uno == item_daily.c.uno)
        .join(duty, duty.c.chain_daily_uno == chain_item_daily.c.chain_daily_uno)
        .join(crew_member, crew_member.c.tlc == duty.c.tlc)
        .where(
            sa.and_(
                item_daily.c.airline == data['airline_iata_code'],
                item_daily.c.day_of_origin == data['flight_origin_date'],
                item_daily.c.flight_no == data['flight_number'],
                item_daily.c.airport_c_is_dep == data['origin_iata'],
            )))
    result = engine.execute(query)
    keys = ['last_name', 'first_name', 'employee_number', 'seat']
    crewmembers = [dict(zip_longest(keys, row)) for row in engine.execute(query)]
    result = CrewMemberResult(crewmembers, query, data, engine)
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

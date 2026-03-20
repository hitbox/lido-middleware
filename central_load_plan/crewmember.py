import argparse
import json
import logging
import sys

from datetime import date
from datetime import datetime
from datetime import time
from types import SimpleNamespace

import oracledb
import sqlalchemy as sa

from sqlalchemy.exc import OperationalError

from central_load_plan.models.lsyrept import ChainItemDaily
from central_load_plan.models.lsyrept import CrewMember
from central_load_plan.models.lsyrept import Duty
from central_load_plan.models.lsyrept import ItemDaily
from central_load_plan.models.lsyrept import NonCrewMember
from central_load_plan.models.lsyrept import RemarkOfEvent

override_driver = None
if sa.__version__.startswith('1'):
    pass
    # # oracledb compatibility with sqlalchemy
    # # https://stackoverflow.com/a/74105559/2680592
    # oracledb.version = "8.3.0"
    # sys.modules["cx_Oracle"] = oracledb
    # override_driver = 'oracle'

JUMPSEAT_KEYS = ('first_name', 'last_name', 'employee_number', 'seat', 'seat_order')

logger = logging.getLogger(__name__)

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
    person_type = substring_between_bars[0]
    remaining = substring_between_bars[1:]
    return (person_type, remaining)

def parse_for_other(string):
    """
    Parse jump seats for type O(ther).
    """
    values = string.split(';')
    if len(values) != len(JUMPSEAT_KEYS):
        # strict=True not supported
        raise ValueError('zip args not equal')
    person_dict = dict(zip(JUMPSEAT_KEYS, values))
    person_dict['employee_number'] = ''
    person_dict['seat'] = 'ACM'
    person_dict['seat_order'] = '999'
    return person_dict

def get_tables(engine):
    metadata = sa.MetaData()
    result = SimpleNamespace(
        chain_item_daily = sa.Table('chain_item_daily', metadata, autoload_with=engine),
        crew_member = sa.Table('crew_member', metadata, autoload_with=engine),
        non_crew_member = sa.Table('non_crew_member', metadata, autoload_with=engine),
        duty = sa.Table('duty', metadata, autoload_with=engine),
        item_daily = sa.Table('item_daily', metadata, autoload_with=engine),
        remark_of_event = sa.Table('remark_of_event', metadata, autoload_with=engine),
    )
    return result

def get_crew_query(data):
    """
    :param data: data as scraped from XML
    """
    crew_query = (
        sa.select(
            CrewMember.trimmed_name().label('last_name'),
            CrewMember.trimmed_first_name().label('first_name'),
            CrewMember.trimmed_employee_no().label('employee_number'),
            Duty.seat_case(ItemDaily.is_leg).label('seat'),
            Duty.seat_order_case(ItemDaily.is_leg, ItemDaily.is_deadhead).label('seat_order'),
            sa.literal('item_daily').label('source'),
        )
        .select_from(ItemDaily)
        .join(
            ChainItemDaily,
            ChainItemDaily.item_daily_uno == ItemDaily.uno,
        )
        .join(
            Duty,
            Duty.chain_daily_uno == ChainItemDaily.chain_daily_uno,
        )
        .join(
            CrewMember,
            CrewMember.tlc == Duty.tlc,
        )
        .where(
            ItemDaily.matches_flight(data)
        )
        .order_by('seat_order')
    )
    return crew_query

def get_jumpseats_query(data):
    return (
        sa.select(RemarkOfEvent.remark)
        .join(ItemDaily, RemarkOfEvent.uno == ItemDaily.uno)
        .where(
            ItemDaily.matches_flight(data),
            RemarkOfEvent.is_jumpseat,
        )
    )

def get_deadheads_query(data):
    # Incident 31169: some dead heads missing.
    return (
        sa.select(
            CrewMember.trimmed_name().label('last_name'),
            CrewMember.trimmed_first_name().label('first_name'),
            CrewMember.trimmed_employee_no().label('employee_number'),
            sa.literal('ACM').label('seat'),
            sa.literal(999).label('seat_order'),
            sa.literal('duty').label('source'),
        )
        .join(Duty, Duty.tlc == CrewMember.tlc)
        .join(ItemDaily, Duty.chain_daily_uno == ItemDaily.chain_daily_uno)
        .where(
            ItemDaily.matches_flight(data),
            Duty.is_deadhead,
        )
    )

def get_person_query(person_model, person_id, employee_number_field):
    query = sa.select(
        # first/last indexes reversed from O(ther) jump seats
        # last_name
        person_model.trimmed_first_name().label(JUMPSEAT_KEYS[1]),
        # first_name
        person_model.trimmed_name().label(JUMPSEAT_KEYS[0]),
        # employee_number
        person_model.trimmed_employee_no().label(JUMPSEAT_KEYS[2]),
        # seat
        sa.literal_column("'ACM'", type_=sa.String()).label(JUMPSEAT_KEYS[3]),
        # seat_order
        sa.literal_column('999', type_=sa.Integer()).label(JUMPSEAT_KEYS[4]),
        sa.literal(person_model.name).label('source'),
    ).where(
        employee_number_field == person_id
    )
    return query

def get_engine(dbconfig):
    if dbconfig and 'oracle_lib_dir' in dbconfig:
        oracle_lib_dir = dbconfig['oracle_lib_dir']

    # connect
    keys = ['username', 'password', 'host', 'port', 'database', 'query', 'drivername']
    connection_config = {key: val for key, val in dbconfig.items() if key in keys}
    if override_driver:
        drivername = override_driver
    if 'query' in connection_config:
        connection_config['query'] = eval(connection_config['query'])
    url = sa.URL.create(**connection_config)
    engine = sa.create_engine(url, max_identifier_length=128)
    return engine

def fromdata(dbconfig, data, dbconfig_fallback=None):
    """
    Return airline specific, object containing crewmembers in list.
    """
    airline_code = data['airline_iata_code']

    for dbconf in [dbconfig, dbconfig_fallback]:
        if dbconf:
            try:
                engine = get_engine(dbconf.get(airline_code, {}))
                engine.connect()
                logger.info('%s', engine)
                break
            except OperationalError:
                logger.debug('Database connection failed. %s', dbconf)

    tables = get_tables(engine)
    crew_query = get_crew_query(data)
    jumpseats_query = get_jumpseats_query(data)
    deadheads_query = get_deadheads_query(data)

    person_tables = {
        # (table, field for person id)
        'C': (
            tables.crew_member,
            tables.crew_member.c.employee_no
        ),
        'N': (
            tables.non_crew_member,
            tables.non_crew_member.c.employee_id
        ),
    }
    with engine.connect() as conn:
        # add crew members first
        crewmembers = conn.execute(crew_query).mappings().fetchall()
        # add jump seat people substrings
        jumpseats = [
            jumpseat_type_and_remaining(jumpseat_str)
            for result in conn.execute(jumpseats_query)
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
                table, employee_number_field = person_tables[person_type]
                person_query = get_person_query(table, person_id, employee_number_field)
                for jumpseat in conn.execute(person_query):
                    crewmembers.append(jumpseat._mapping)
        # add deadheads from duty
        for person in conn.execute(deadheads_query):
            crewmembers.append(person._mapping)

        result = CrewMemberResult(crewmembers, crew_query, data, engine)
        return result

def fromdata(session, data):
    crew_query = get_crew_query(data)
    for row in session.scalars(crew_query):
        pass

def main(argv=None):
    parser = argparse.ArgumentParser(
        'Debug queries for looking up crewmembers.',
    )
    parser.add_argument(
        'airline_iata_code',
    )
    parser.add_argument(
        'flight_origin_date',
        type = date.fromisoformat,
    )
    parser.add_argument(
        'flight_number',
        type = int,
    )
    parser.add_argument(
        'origin_iata',
    )
    parser.add_argument(
        'scheduled_departure_time',
        type = datetime.fromisoformat,
    )
    parser.add_argument(
        '--database',
        type = json.loads
    )
    args = parser.parse_args(argv)
    dbconfig = args.database
    delattr(args, 'database')

    flight_data = vars(args)
    from pprint import pprint
    pprint(flight_data)
    fromdata(dbconfig, flight_data)

if __name__ == '__main__':
    main()

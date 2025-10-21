import logging
import sys

from types import SimpleNamespace

import oracledb
import sqlalchemy as sa

from sqlalchemy.exc import OperationalError

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

def get_crew_query(tables, data):
    """
    :param tables: attribute access tables
    :param data: data as scraped from XML
    """
    crew_member = tables.crew_member
    item_daily = tables.item_daily
    chain_item_daily = tables.chain_item_daily
    duty = tables.duty

    is_type_leg = item_daily.c.type == 'L'
    is_type_deadhead = item_daily.c.type == 'F'

    crew_query = (
        sa.select(
            sa.func.trim(crew_member.c.name).label('last_name'),
            sa.func.trim(crew_member.c.first_name).label('first_name'),
            sa.func.trim(crew_member.c.employee_no).label('employee_number'),
            sa.case(
                (sa.and_(is_type_leg, duty.c.assigned_rank == 0), 'PIC'),
                (sa.and_(is_type_leg, duty.c.assigned_rank == 1), 'SIC'),
                (sa.and_(is_type_leg, duty.c.assigned_rank == 2), 'IRO'),
                (sa.and_(is_type_leg, duty.c.assigned_rank == 3), 'CP'),
                (sa.and_(is_type_leg, duty.c.assigned_rank == 5), 'FA'),
                else_ = 'ACM',
            ).label('seat'),
            sa.case(
                (is_type_leg, duty.c.assigned_rank),
                (is_type_deadhead, 99),
            ).label('seat_order'),
            sa.literal('item_daily').label('source'),
        )
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
        ).filter(
            item_daily.c.airline == data['airline_iata_code'],
            item_daily.c.day_of_origin == data['flight_origin_date'],
            item_daily.c.flight_no == data['flight_number'],
            item_daily.c.airport_c_is_dep == data['origin_iata'],
            item_daily.c.departure_date_scd == data['scheduled_departure_time'].date(),
            # departure_time_scd is stored as CHAR(4)
            item_daily.c.departure_time_scd == data['scheduled_departure_time'].strftime('%H%M'),
        ).order_by('seat_order')
    )
    return crew_query

def get_jumpseats_query(tables, data):
    remark_of_event = tables.remark_of_event
    item_daily = tables.item_daily
    jumpseats_query = (
        sa.select(
            remark_of_event.c.remark,
        ).select_from(
            item_daily
        ).join(
            remark_of_event,
            remark_of_event.c.uno == item_daily.c.uno
        ).filter(
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
    )
    return jumpseats_query

def get_deadheads_query(tables, data):
    # Incident 31169: some dead heads missing.
    crew_member = tables.crew_member
    duty = tables.duty
    deadheads_query = (
        sa.select(
            sa.func.trim(crew_member.c.name).label('last_name'),
            sa.func.trim(crew_member.c.first_name).label('first_name'),
            sa.func.trim(crew_member.c.employee_no).label('employee_number'),
            # seat (deadhead)
            sa.literal_column("'ACM'", type_=sa.String()).label(JUMPSEAT_KEYS[3]),
            # seat_order
            sa.literal_column('999', type_=sa.Integer()).label(JUMPSEAT_KEYS[4]),
            sa.literal('duty').label('source'),
        ).join(
            duty,
            duty.c.tlc == crew_member.c.tlc
        ).filter(
            duty.c.airline == data['airline_iata_code'],
            duty.c.day_of_origin == data['flight_origin_date'],
            duty.c.flight_no == data['flight_number'],
            duty.c.airport_c_is_dep == data['origin_iata'],
            duty.c.departure_date_scd == data['scheduled_departure_time'].date(),
            # departure_time_scd is stored as CHAR(4)
            duty.c.departure_time_scd == data['scheduled_departure_time'].strftime('%H%M'),
            duty.c.type == 'F', # deadhead
        )
    )
    return deadheads_query

def get_person_query(table, person_id, employee_number_field):
    query = sa.select(
        # first/last indexes reversed from O(ther) jump seats
        # last_name
        sa.func.trim(table.c.name).label(JUMPSEAT_KEYS[1]),
        # first_name
        sa.func.trim(table.c.first_name).label(JUMPSEAT_KEYS[0]),
        # employee_number
        sa.func.trim(employee_number_field).label(JUMPSEAT_KEYS[2]),
        # seat
        sa.literal_column("'ACM'", type_=sa.String()).label(JUMPSEAT_KEYS[3]),
        # seat_order
        sa.literal_column('999', type_=sa.Integer()).label(JUMPSEAT_KEYS[4]),
        sa.literal(table.name).label('source'),
    ).where(
        employee_number_field == person_id
    )
    return query

def get_engine(dbconfig):
    if 'oracle_lib_dir' in dbconfig:
        oracle_lib_dir = dbconfig['oracle_lib_dir']
        #try:
        #    oracledb.init_oracle_client(lib_dir=oracle_lib_dir)
        #except oracledb.ProgrammingError:
        #    # already initialized
        #    pass

    # connect
    keys = ['username', 'password', 'host', 'port', 'database', 'query', 'drivername']
    connection_config = {key: val for key, val in dbconfig.items() if key in keys}
    if override_driver:
        drivername = override_driver
    if 'query' in connection_config:
        connection_config['query'] = eval(connection_config['query'])
    url = sa.engine.URL.create(**connection_config)
    engine = sa.create_engine(url, max_identifier_length=128)
    return engine

def fromdata(dbconfig, data, dbconfig_fallback=None):
    """
    Return airline specific, object containing crewmembers in list.
    """
    airline_code = data['airline_iata_code']

    for dbconf in [dbconfig, dbconfig_fallback]:
        airline_dbconfig = dbconf[airline_code]
        try:
            engine = get_engine(airline_dbconfig)
            engine.connect()
            logger.info('%s', engine)
            break
        except OperationalError:
            logger.debug('Database connection failed. %s', airline_dbconfig)

    tables = get_tables(engine)
    query_crew = get_crew_query(tables, data)
    query_jumpseats = get_jumpseats_query(tables, data)
    query_deadheads = get_deadheads_query(tables, data)

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
        crewmembers = conn.execute(query_crew).mappings().fetchall()
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
                table, employee_number_field = person_tables[person_type]
                person_query = get_person_query(table, person_id, employee_number_field)
                for jumpseat in conn.execute(person_query):
                    crewmembers.append(jumpseat._mapping)
        # add deadheads from duty
        for person in conn.execute(query_deadheads):
            crewmembers.append(person._mapping)

        result = CrewMemberResult(crewmembers, query_crew, data, engine)
        return result

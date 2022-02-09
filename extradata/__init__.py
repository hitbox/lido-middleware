import csv

from collections import defaultdict
from pathlib import Path

class ExtradataError(Exception):
    pass


class AircraftRegistrationAirlineMapping:
    """
    Map aircraft registration (tail) to airline.
    """

    def __init__(self):
        import warnings
        warnings.warn('Temporary defaultdict implementation')
        self.airline = defaultdict(lambda:'ABX')


def _or_none(v):
    """
    Return the value `v` if truthy or None.
    """
    return v if v else None

class AirlineDesignators:
    """
    Access to company/airline designator mappings in both directions.

    airline_designators.by_company[company] -> airline code
    airline_designators.by_airline[airline] -> company code
    """

    def __init__(self):
        path = Path(__file__).parent / 'airline_designators.csv'
        with open(path, newline='') as fp:
            # company -> airline
            self.by_company = {k: _or_none(v) for k, v in csv.reader(fp) if k}
            # airline -> company
            self.by_airline = {v: _or_none(k) for k, v in self.by_company.items() if v}
            # companies
            self.company_codes = [c for c in self.by_company if c]
            # airlines
            self.airline_codes = [a for a in self.by_airline if a]
            # companies + airlines
            self.all_codes = self.company_codes + self.airline_codes

    def split_company_or_airline_and_flight_number(self, s):
        """
        :param s: string that starts with an airline or company and ends with a
                  flight number.
        """
        matches = [code for code in self.all_codes if s.startswith(code)]
        nmatches = len(matches)
        if nmatches == 0:
            raise ExtradataError(
                'No matches for airline or company, %r' % s)
        elif nmatches > 1:
            raise ExtradataError(
                'More than one match for airline or company, %r, %r' % (s, matches))
        else:
            # one match, is it the company or airline?
            match = matches[0]
            is_company = match in self.company_codes
            is_airline = match in self.airline_codes
            if is_company and is_airline:
                raise ExtradataError(
                    'Code matches both company and airline, %r' % match)
            data = {'flight_number': s[len(match):]}
            if is_company:
                data['company'] = match
                data['airline_designator'] = self.by_company[match]
            else:
                data['company'] = self.by_airline[match]
                data['airline_designator'] = match
            return data


class Stations:
    """
    Mappings to-from iata/icao.
    """

    _station_types = ['iata', 'icao']
    _opposite_station_type = {'iata': 'icao', 'icao': 'iata'}

    def __init__(self):
        path = Path(__file__).parent / 'iata2icao.csv'
        with open(path, newline='') as fp:
            self.iata2icao = dict(csv.reader(fp))
            self.icao2iata = {v: k for k, v in self.iata2icao.items()}
            self.iata_stations = list(self.iata2icao)
            self.icao_stations = list(self.icao2iata)
            self.all_stations = self.iata_stations + self.icao_stations
            self._opposite_station_lookup = {
                'iata': self.iata2icao,
                'icao': self.icao2iata}

    def detect_code_type(self, station):
        if station not in self.all_stations:
            raise ExtradataError('Unrecognized station, %r' % station)
        # :but not in both
        is_iata = station in self.iata_stations
        is_icao = station in self.icao_stations
        if is_iata and is_icao:
            raise ExtradataError(
                'Station detected as both IATA and ICAO, %r' % station)
        return 'iata' if is_iata else 'icao'

    def filled(self, station):
        """
        Return {'iata': ..., 'icao': ...} by detecting if `station` is iata or
        icao and filling the other.
        """
        if self.detect_code_type(station) == 'iata':
            return {'iata': station, 'icao': self.iata2icao[station]}
        else:
            return {'iata': self.icao2iata[station], 'icao': station}


class NetlineAircraftRegistrationAirlineMapping:
    """
    Get aircraft registration from Netline database
    """

    def __init__(self, drivername, host, username, password, database, port=None):
        self.drivername = drivername
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = port
        self._airline = None

    def _init_airline(self):
        import sqlalchemy as sa
        url = sa.engine.url.URL(
            drivername = self.drivername,
            host = self.host,
            username = self.username,
            password = self.password,
            database = self.database,
            port = self.port)
        engine = sa.create_engine(url, max_identifier_length=128)
        conn = engine.connect()
        metadata = sa.MetaData()
        # see: NetLine_Crew Core Data Model 2020.2.pdf
        aircraft = sa.Table('aircraft', metadata, autoload_with=engine)
        columns = [aircraft.c.registration, aircraft.c.ac_owner, aircraft.c.ac_operator]
        query = sa.sql.select(columns)
        result = {registration: operator for registration, owner, operator in conn.execute(query)}
        self._airline = result

    @property
    def airline(self):
        if self._airline is None:
            self._init_airline()
        return self._airline


aircraftregistration = AircraftRegistrationAirlineMapping()
airline_designators = AirlineDesignators()
stations = Stations()

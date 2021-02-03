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


class AirlineDesignators:
    """
    Access to company/airline designator mappings in both directions.

    airline_designators.by_company[company] -> airline code
    airline_designators.by_airline[airline] -> company code
    """

    def __init__(self):
        path = Path(__file__).parent / 'airline_designators.csv'
        with open(path, newline='') as fp:
            self.by_company = dict(csv.reader(fp))
            self.by_airline = {v: k for k, v in self.by_company.items()}
            self.company_codes = list(self.by_company)
            self.airline_codes = list(self.by_airline)
            self.all_codes = self.company_codes + self.airline_codes


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


aircraftregistration = AircraftRegistrationAirlineMapping()
airline_designators = AirlineDesignators()
stations = Stations()

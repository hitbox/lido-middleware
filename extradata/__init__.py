import csv

from pathlib import Path

class ExtradataError(Exception):
    """
    """


def trash():
    def _iata2icao_csvfile():
        return open(Path(__file__).parent / 'iata2icao.csv', newline='')

    def iata2icao():
        with _iata2icao_csvfile() as fp:
            return {iata: icao for iata, icao in csv.reader(fp)}

    def icao2iata():
        with _iata2icao_csvfile() as fp:
            return {icao: iata for iata, icao in csv.reader(fp)}

class Stations:

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

    def update_other_station_by_type(self, data, prefix, sep='_'):
        """
        Update the IATA/ICAO station that is not already set, INPLACE. Both may
        not be set.
        """
        source_keys = [prefix + sep + postfix for postfix in self._station_types]
        values = [data[source_key] for source_key in source_keys]
        if all(values):
            raise ExtradataError('Both types of stations already set')
        for station_type in self._station_types:
            value = data.get(prefix + sep + station_type)
            if value is not None:
                lookup = self._opposite_station_lookup[station_type]
                opposite_type = self._opposite_station_type[station_type]
                data[prefix + sep + opposite_type] = lookup[value]


class AirlineDesignators:
    """
    Access to company/airline mappings in both directions.

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


stations = Stations()
airline_designators = AirlineDesignators()

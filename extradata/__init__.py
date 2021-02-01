import csv

from pathlib import Path

def _iata2icao_csvfile():
    return open(Path(__file__).parent / 'iata2icao.csv', newline='')

def iata2icao():
    with _iata2icao_csvfile() as fp:
        return {iata: icao for iata, icao in csv.reader(fp)}

def icao2iata():
    with _iata2icao_csvfile() as fp:
        return {icao: iata for iata, icao in csv.reader(fp)}

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


airline_designators = AirlineDesignators()

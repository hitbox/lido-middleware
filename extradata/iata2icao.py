import argparse
import configparser
import csv

from operator import itemgetter

import sqlalchemy as sa

def main(argv=None):
    """
    CLI for iata2icao.csv
    """
    parser = argparse.ArgumentParser(
        description = main.__doc__,
    )
    parser.add_argument('config')
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    csvpath = cp['iata2icao']['csvdb']
    reader = csv.reader(open(csvpath, newline=''))
    existing = dict((iata.strip(), icao.strip()) for iata, icao in reader)
    original = existing.copy()

    keys = cp['iata2icao']['keys'].replace(',', ' ').split()
    new = []
    updates = []
    data = dict()
    for key in keys:
        url = sa.engine.url.URL.create(
            drivername = cp[key]['drivername'],
            host = cp[key]['host'],
            username = cp[key]['username'],
            password = cp[key]['password'],
            database = cp[key]['database'],
            port = cp[key]['port']
        )
        engine = sa.create_engine(url, max_identifier_length=128)
        metadata = sa.MetaData()
        airport_imf = sa.Table('airport_imf', metadata, autoload_with=engine)
        with engine.connect() as conn:
            statement = sa.select([
                sa.func.trim(airport_imf.c.ap_name).label('ap_name'),
                airport_imf.c.iata_ap_code,
                airport_imf.c.icao_code,
            ])
            result = conn.execute(statement)
            for ap_name, iata, icao in result:
                if iata not in existing or existing[iata] == '':
                    existing[iata] = icao
                    new.append((url.username, ap_name, iata, icao))
                elif icao != existing[iata]:
                    updates.append((url.username, ap_name, iata, existing[iata], icao))
                    existing[iata] = icao

    iatakey = itemgetter(2)
    if new:
        print('new')
        for source, ap_name, iata, icao in sorted(new, key=iatakey):
            print(f'{source=}, {iata=} + {icao=} ({ap_name})')

    if updates:
        print('updates')
        for source, ap_name, iata, original_icao, icao in sorted(updates, key=iatakey):
            print(f'{source=}, {iata=} {original_icao!r} -> {icao!r} ({ap_name})')

if __name__ == '__main__':
    main()

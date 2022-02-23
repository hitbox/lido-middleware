import argparse
import configparser
import datetime
import os
import pickle
import types
import xml.etree.ElementTree as ET

from itertools import chain
from pathlib import Path

wab_filename_fields = [
    'prefix',
    'source',
    'timestamp_in_gmt',
    'company',
    'flight_number',
    'origin_iata',
    'destination_iata',
    'now_datetime',
]

wab_filename_types = dict(
    timestamp_in_gmt = lambda s: datetime.datetime.strptime(s, '%d%b%Y%H%M%S'),
    now_datetime = lambda s: datetime.datetime.strptime(s, '%Y%m%d%H%M%S.%f'),
)

pax_filename_fields = [
    'prefix',
    'company',
    'flight_number',
    'now_datetime',
]

pax_filename_types = dict(
    # no microseconds as above
    now_datetime = lambda s: datetime.datetime.strptime(s, '%d%b%Y%H%M%S'),
)

def parse_filename(path, fields, typemap):
    values = path.stem.split('_')
    datadict = dict(zip(fields, values))
    for field, typefunc in typemap.items():
        datadict[field] = typefunc(datadict[field])
    datadict['path'] = path
    return datadict

def parse_wabfn(path):
    """
    Return dict of data scraped from WAB filename.
    """
    return parse_filename(path, wab_filename_fields, wab_filename_types)

def parse_paxfn_and_xml(path):
    """
    Return dict of data scraped from PaxDetail filename and XML source.
    """
    paxdata_dict = parse_filename(path, pax_filename_fields, pax_filename_types)
    tree = ET.parse(path)
    root = tree.getroot()
    # confirmed iata in paxdetail.output
    paxdata_dict['origin_iata'] = root.find('./messages/paxDetail/legId/depApSched').text
    paxdata_dict['date_of_origin'] = root.find('./messages/paxDetail/legId/dayOfOrigin').text
    return paxdata_dict

def matchdata(wabdata_dict, paxdata_dict):
    """
    Match on data scraped from filenames.
    """
    return (
        wabdata_dict['company'] == paxdata_dict['company']
        and wabdata_dict['flight_number'] == paxdata_dict['flight_number']
        and wabdata_dict['origin_iata'] == paxdata_dict['origin_iata']
    )

def load_data(config):
    """
    """
    wabdir = Path(config.wabsource)
    paxdir = Path(config.paxdetailsource)
    wabdata = []
    paxdata = []
    # WAB
    for wabpath in wabdir.iterdir():
        wabdata_dict = parse_wabfn(wabpath)
        wabdata_dict['matches'] = []
        wabdata.append(wabdata_dict)
    # PaxDetail
    for paxpath in paxdir.iterdir():
        paxdata_dict = parse_paxfn_and_xml(paxpath)
        paxdata_dict['matches'] = []
        paxdata.append(paxdata_dict)
    return (wabdata, paxdata)

def match_data(wabdata, paxdata):
    for wabdata_dict in wabdata:
        for paxdata_dict in paxdata:
            if matchdata(wabdata_dict, paxdata_dict):
                wabdata_dict['matches'].append(paxdata_dict)
                paxdata_dict['matches'].append(wabdata_dict)
    return (wabdata, paxdata)

def main(argv=None):
    """
    Parse WAB filenames and match against PaxDetail XML.
    """
    parser = argparse.ArgumentParser(prog='matchruns', description=main.__doc__)
    parser.add_argument('config', nargs='+')
    parser.add_argument('--load', help='Load data from pickle.')
    parser.add_argument('--save', help='Save data to pickle.')
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    config = types.SimpleNamespace(
        wabsource = cp['matchruns']['wabsource'],
        paxdetailsource = cp['matchruns']['paxdetailsource'],
    )

    if args.load and Path(args.load).exists():
        with open(args.load, 'rb') as fp:
            wabdata, paxdata = pickle.load(fp)
    else:
        wabdata, paxdata = load_data(config)
        if args.save:
            with open(args.save, 'wb') as fp:
                pickle.dump((wabdata, paxdata), fp)

    # modifies the dicts
    match_data(wabdata, paxdata)
    import code
    context = globals()
    context.update(locals())
    del context['context']
    code.interact(local=context)

if __name__ == '__main__':
    main()

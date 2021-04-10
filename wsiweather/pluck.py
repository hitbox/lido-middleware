import argparse
import configparser
import re
import sys
import textwrap
import traceback
import xml.etree.ElementTree as ET

from pprint import pprint

validity_line_re = re.compile('(?P<start_of_validity>\d{4})/(?P<end_of_validity>\d{4})')

def fromxml(root):
    data = {}
    elem = root.find('.//{*}taf_reports/{*}icao_site_id')
    data['icao_originator'] = elem.text

    elem = root.find('.//{*}taf_reports/{*}issue_time')
    data['time_of_observation'] = elem.text

    elem = root.find('.//{*}taf_reports/{*}undecoded_groups')
    data['remark'] = elem.text

    elem = root.find('.//{*}taf_reports/{*}data')
    data_lines = elem.text.splitlines()
    match = validity_line_re.search(data_lines[0])
    validity_data = match.groupdict()
    # something of a datetime: %d%H00
    data.update({key: value + '00' for key, value in validity_data.items()})

    # keep after the end_of_validity plus a space
    data_lines[0] = data_lines[0][match.end()+1:]
    # there seemed to be some effort to dedent in the example
    data_lines[1:] = textwrap.dedent('\n'.join(data_lines[1:])).splitlines()

    data['weather_text'] = '\n'.join(data_lines)
    # there seemed to be an effort to right-strip whitespace in the example
    data['weather_text'] = data['weather_text'].rstrip()

    return data

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('xmlfiles', nargs='+')
    args = parser.parse_args(argv)

    for xmlfile in args.xmlfiles:
        print(xmlfile)
        try:
            tree = ET.parse(xmlfile)
        except ET.ParseError:
            traceback.print_exc(file=sys.stdout)
        else:
            root = tree.getroot()
            data = fromxml(root)
            pprint(data)

if __name__ == '__main__':
    main()

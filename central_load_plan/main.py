import argparse
import configparser
import sys
import traceback
import xml.etree.ElementTree as ET

from . import crewmember
from . import email
from . import pluck
from . import schema

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('config', nargs='+')
    parser.add_argument('xmlfiles', nargs='+')
    args = parser.parse_args(argv)

    cp = configparser.ConfigParser()
    cp.read(args.config)

    for xmlfile in args.xmlfiles:
        try:
            tree = ET.parse(xmlfile)
        except ET.ParseError:
            traceback.print_exc(file=sys.stdout)
        else:
            root = tree.getroot()
            data = pluck.fromxml(root)
            data = schema.OperationalFlightPlanSchema().load(data)
            # hit database for crew members
            data['crewmembers'] = crewmember.fromdata(cp, data)
            print(email.render(data))

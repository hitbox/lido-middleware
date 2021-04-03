import argparse
import sys
import traceback
import xml.etree.ElementTree as ET

from . import email
from . import pluck
from .schema import OperationalFlightPlanSchema

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

            data = pluck.fromxml(root)
            # patch in temp data
            data['crewmembers'] = [
                dict(
                    seat = 'PIC',
                    first_name = 'Carlos',
                    last_name = 'Ortiz-Longo',
                    employee_number = '453771',
                ),
                dict(
                    seat = 'SIC',
                    first_name = 'Ignacio',
                    last_name = 'Perez Losada',
                    employee_number = '454744',
                ),
            ]

            schema = OperationalFlightPlanSchema()
            data = schema.load(data)

            print(email.render(data))

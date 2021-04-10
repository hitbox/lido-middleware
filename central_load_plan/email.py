import argparse
import sys
import textwrap
import xml.etree.ElementTree as ET

from . import pluck
from . import schema

def render(data):
    """
    Render the central load plan email.

    :param data: fully marshalled into Python data types, data.
    """
    # Tried using a jinja template for this. It worked well. The document was
    # apparent at a glance. Not using it because Vim (nvim) refused to
    # cooperate in NOT always reflowing my text. It was so aggravating that
    # this build-by-lines in Python was chosen.
    lines = []

    lines.append('')
    lines.append(
        'LEG DEPARTURE DATE (UTC): '
        + data['leg_departure_date_utc'].strftime('%d%b%y (%H%MZ)').upper()
        + ' REV NO: %s' % data['version_number']
    )
    lines.append(
        'FLT #   DEST    TAIL #  STE     STD     ETD     ETA     '
    )
    dtfmt = '%d/%H%M'
    lines.append(
        '%-8s' % data['flight_number']
        + '%-8s' % data['destination_iata']
        + '%-8s' % data['aircraft_registration']
        # STE:
        + data['estimated_block_time'].strftime('%H:%M')
        + ' ' * 3
        + data['scheduled_departure_time'].strftime(dtfmt)
        + ' '
        + data['estimated_departure_time'].strftime(dtfmt)
        + ' '
        + data['estimated_arrival_time'].strftime(dtfmt)
    )

    lines.append('')
    lines.append(
        '*** ALL PAYLOAD AND FUEL DATA BELOW IN {LBS} ***'
    )
    lines.append(
        '*** BALLAST FUEL IS INCLUDED IN THE  RAMP FUEL VALUE ***'
    )
    lines.append('')

    lines.append(
        'PLND PAYLOAD    RAMP FUEL   FUEL BURN   TAXI FUEL   BALLAST FUEL'
    )
    if data['ballast_fuel'] is None:
        ballast_fuel = '00000'
    else:
        ballast_fuel = data['ballast_fuel']
    lines.append(
        '%-16s' % data['planned_payload']
        + '%-12s' % data['ramp_fuel']
        + '%-12s' % data['fuel_burn']
        + '%-12s' % data['taxi_fuel']
        + '%-12s' % ballast_fuel
    )
    lines.append('')
    lines.append(
        'MAX PAYLOAD     MZFW        MTOW        MLDG'
    )
    lines.append(
        '%-16s' % data['max_payload']
        + '%-12s' % data['mzfw']
        + '%-12s' % data['mtow']
        + '%-12s' % data['mldg']
    )
    lines.append('')
    lines.append(
        'SEAT    FIRST NAME      LAST NAME       EMPLOYEE #'
    )
    lines.append(
        '----    ----------      ---------       ----------'
    )
    for crew in data['crewmembers']:
        lines.append(
            '%-8s' % crew['seat']
            + '%-16s' % crew['first_name']
            + '%-16s' % crew['last_name']
            + '%-12s' % crew['employee_number']
        )

    lines.append('')
    lines.append(
        '--- A/C EQUIPMENT STATUS ---'
    )
    lines.append(
        'ITEM          DESCRIPTION'
    )
    for status in data['aircraft_equipment_status']:
        line = '%-14s' % status['item']
        if status['description']:
            line += '\n'.join(
                textwrap.wrap(status['description'],
                              width=80-14,
                              subsequent_indent=' ' * 14)
            )
        lines.append(line)

    lines.append('')
    lines.append(
        '*** OFP IS THE CONTROLLING DOCUMENT FOR DATA PRODUCED FOR THIS MESSAGE. ***'
    )

    return '\n'.join(lines)

def main(argv=None):
    """
    Produce email text from XML file minus the crewmembers.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('xmlfiles', nargs='+')
    args = parser.parse_args(argv)

    for xmlfile in args.xmlfiles:
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        data = pluck.fromxml(root)
        data = schema.OperationalFlightPlanSchema().load(data)
        print(email.render(data))

if __name__ == '__main__':
    sys.exit(main())

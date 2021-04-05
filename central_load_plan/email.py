import textwrap

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

    dtfmt = '{d.day:0>2}/{d.hour:0>2}{d.minute:0>2} '

    lines.append('')
    lines.append(
        'LEG DEPARTURE DATE (UTC): '
        + data['leg_departure_date_utc'].strftime('%d%b%y (%H%MZ)').upper()
        + ' REV NO: %s' % data['version_number']
    )
    lines.append(
        'FLT #   DEST    TAIL #  STE     STD     ETD     ETA     '
    )
    lines.append(
        '%-8s' % data['flight_number']
        + '%-8s' % data['destination_iata']
        + '%-8s' % data['aircraft_registration']
        + '{t.hour:0>2}:{t.minute:0>2}'.format(t=data['estimated_arrival_time'])
        + '   '
        + dtfmt.format(d=data['scheduled_departure_time'])
        + dtfmt.format(d=data['estimated_departure_time'])
        + dtfmt.format(d=data['estimated_arrival_time'])
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
    lines.append(
        '%-16s' % data['planned_payload']
        + '%-12s' % data['ramp_fuel']
        + '%-12s' % data['fuel_burn']
        + '%-12s' % data['taxi_fuel']
        + '' if not data['ballast_fuel'] else '%-12s' % data['ballast_fuel']
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
        'Until further notice no inoperative or missing locks in ULD positions A7 thru K12.'
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
                textwrap.wrap(status['description'], subsequent_indent=' ' * 14)
            )
        lines.append(line)

    lines.append('')
    lines.append(
        '*** OFP IS THE CONTROLLING DOCUMENT FOR DATA PRODUCED FOR THIS MESSAGE. ***'
    )

    return '\n'.join(lines)

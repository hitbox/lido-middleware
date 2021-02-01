import re

from .exceptions import SableParseError
from .regex import dense_data_line_re
from .regex import get_airline_flight_number_re
from .regex import header_re
from .regex import si_load_re

from extradata import airline_designators

HEADER = ['POS', 'DST', 'ULDNUMBER', 'TARE', 'NETT', 'TOTAL', 'FLAG', 'VOL']

position_spans = [
    (1, 4), # POS
    (5, 8), # DST
    (9, 19), # ULDNUMBER
    (20, 24), # TARE
    (24, 30), # NETT
    (30, 35), # TOTAL
    (36, 60), # FLAG
    (66, 71), # VOL
]


def parse_from_text(text):
    """
    Parse Sable load plan message.
    """
    lines = iter(text.splitlines())
    sable_data = {}
    # find and parse a line of densely packed data.
    # <airline or company and flight number>
    # /<day>.<tail>.<origin_iata>-<destination_iata>
    for line in lines:
        match = dense_data_line_re.match(line)
        if match:
            dense_line_data = match.groupdict()
            # further parsing below...
            break
    else:
        raise SableParseError(
            'Unable to find and parse dense data line, %r' % line)
    # add keys other than the airline/flight number
    for key in ['day', 'tail', 'origin_iata', 'destination_iata']:
        sable_data[key] = dense_line_data[key]
    # parse company/airline designator from flight number
    flight_number = dense_line_data['airline_and_flight_number']
    # have observed both company code and airline code in the messages.
    # construct pattern that will match either.
    airline_flight_number_re = get_airline_flight_number_re()
    match = airline_flight_number_re.match(flight_number)
    if not match:
        raise SableParseError(
            'Unable to parse airline and flight number, %r' % flight_number)
    airline_flight_number_data = match.groupdict()
    sable_data['flight_number'] = airline_flight_number_data['flight_number']

    # determine what kind of data was in front of the flight number and set it
    # to the appropriate key AND set the other key.
    company_or_airline_code = airline_flight_number_data['company_or_airline_code']
    if company_or_airline_code in airline_designators.company_codes:
        sable_data['company'] = company_or_airline_code
        sable_data['airline_designator'] = airline_designators.by_company[sable_data['company']]
    elif company_or_airline_code in airline_designators.airline_codes:
        sable_data['airline_designator'] = company_or_airline_code
        sable_data['company'] = airline_designators.by_airline[sable_data['airline_designator']]
    else:
        raise SableParseError(
            'Unable to determine if value is a company code or an airline'
            ' designator, %r' % company_or_airline_code)

    # SI LOAD information line
    line = next(lines)
    match = si_load_re.match(line)
    if not match:
        raise SableParseError(
            'Unable to parse SI LOAD information line, %r' % line)
    sable_data.update(match.groupdict())

    # find position data header line
    for line in lines:
        match = header_re.match(line)
        if match:
            spans = enumerate(match.groups(), start=1)
            spans = [match.span(group) for group, _ in spans]
            break
    else:
        raise SableParseError('Positions data header line not found.')

    # scrape position data
    positions = []
    for line in lines:
        if not line.startswith(':'):
            break
        # split on span positions
        row = [line[s:e] for s, e in position_spans]
        # dict-ify
        row = dict(zip(HEADER, row))
        # strip string values
        row = {k: v.strip() for k, v in row.items()}
        # empty string to None
        row = {k: v if v else None for k, v in row.items()}
        positions.append(row)
    sable_data['positions'] = positions

    return sable_data

def loadplan_from_message(message):
    return parse_from_text(message.attachments[0].payload.decode('utf8'))

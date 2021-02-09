import re

from .exceptions import SableParseError
from .regex import dense_data_line_re
from .regex import header_re
from .regex import si_load_re

from extradata import airline_designators
from schema import PRINT_DATETIME_FORMAT

HEADER = ['POS', 'DST', 'ULDNUMBER', 'TARE', 'NETT', 'TOTAL', 'FLAG', 'VOL']

# extract position data by position in string line
# numbers have been observed with no space separating them
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

def from_text(text):
    """
    Extract data from Sable load plan message. Does no data conversion,
    everything is a string.
    """
    lines = iter(text.splitlines())
    sable_data = {}
    # find and parse a line of densely packed data.
    for line in lines:
        match = dense_data_line_re.match(line)
        if match:
            sable_data.update(match.groupdict())
            break
    else:
        raise SableParseError(
            'Unable to find and parse dense data line, %r' % line)

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
            break
    else:
        raise SableParseError('Positions data header line not found.')

    # scrape position data
    positions = []
    for line in lines:
        if not line.startswith(':'):
            break
        # split on span positions and strip whitespace
        row = (line[s:e].strip() for s, e in position_spans)
        # add header and make dict
        row = dict(zip(HEADER, row))
        positions.append(row)
    #sable_data['positions'] = positions

    return sable_data

def loadplan_from_message(message):
    data = from_text(message.attachments[0].payload.decode('utf8'))
    data['message_date'] = message.date.strftime(PRINT_DATETIME_FORMAT)
    return data

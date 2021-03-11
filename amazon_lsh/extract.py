import string

from run.exceptions import ExtractError

from .regex import dense1_re
from .regex import dense2_re
from .regex import dense3_re
from .regex import loadsheet_re
from .regex import weight_position_re
from .regex import weight_re
from .regex import weight_with_max_re

class AmazonLSHExtractError(ExtractError):
    pass


def _raise_for_match(regex, line):
    match = regex.match(line)
    if not match:
        raise AmazonLSHExtractError(
            'Line %r does not match regex %r' % (line, regex))
    return match

def _raise_for_startswith(expect, line):
    if not line.startswith(expect):
        raise AmazonLSHExtractError(
            'Expected line starts with %r, got %r' % (expect, line))

def from_text(text):
    data = {}
    text = ''.join(c for c in text if c in string.printable)
    lines = iter(text.splitlines())

    # skip empty lines in beginning
    for line in lines:
        if line:
            break

    _raise_for_startswith('QN AMZSITA', line)
    _raise_for_startswith('.AMZSITA', next(lines))

    # extract a bunch of title/header type stuff
    regexes = [
        dense1_re,
        loadsheet_re,
        dense2_re,
        dense3_re,
    ]
    for regex, line in zip(regexes, lines):
        match = _raise_for_match(regex, line)
        data.update(match.groupdict())

    line = next(lines)
    if line != '':
        raise AmazonLSHExtractError('Expected empty line, got %r' % line)

    # the next several lines alternate between with max and without.
    regexes = [
        weight_with_max_re,
        weight_re,
        weight_with_max_re,
        weight_re,
        weight_with_max_re,
    ]
    for regex, line in zip(regexes, lines):
        match = _raise_for_match(regex, line)
        linedata = match.groupdict()
        name = linedata['weight_name'].strip()
        data[name] = { 'weight_kg': linedata['weight_kg'] }
        if 'max_kg' in linedata:
            data[name]['max_kg'] = linedata['max_kg']

    _raise_for_startswith('BALANCE AND SEATING', next(lines))

    # tentative approach: split on white space and reraise for unexpected
    # number of results.
    for n, line in enumerate(lines, start=1):
        if n > 20:
            raise AmazonLSHExtractError(
                'More balance and seating lines than expected')
        if line == '':
            break
        items = line.split()
        try:
            name1, weight1, name2, weight2 = items
        except ValueError:
            raise AmazonLSHExtractError(
                'Expected four value after split, got %s on line %r'
                % (len(items), line))
        data[name1] = weight1
        data[name2] = weight2

    _raise_for_startswith('STAB TO', next(lines))
    _raise_for_startswith('', next(lines))

    position_lines = next(lines)
    _raise_for_startswith('T', position_lines)
    # strip leading T, no idea what it means
    position_lines = position_lines[1:]
    for n, line in enumerate(lines, start=1):
        if n > 20:
            raise AmazonLSHExtractError(
                'More position lines than expected')
        if line == '':
            break
        position_lines += line

    positions = []
    for substr in position_lines.split('/'):
        match = weight_position_re.match(substr)
        if not match:
            raise AmazonLSHExtractError('Unable to match %r on %r' % (weight_position_re, substr))
        position_data = match.groupdict()
        if position_data['position']:
            position_data['position'] = position_data['position'].lstrip('.')
        positions.append(position_data)
    data['positions'] = positions

    return data

def loadplan_from_message(message):
    # have observed empty text in messages
    if not message.subject.startswith('LSH'):
        raise AmazonLSHExtractError('message subject does not start with LSH')
    if not message.text.strip():
        raise AmazonLSHExtractError('message text empty')
    return from_text(message.text)

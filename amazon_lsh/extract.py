from run.exceptions import ExtractError

from .regex import dense1_re
from .regex import dense2_re
from .regex import dense3_re
from .regex import loadsheet_re
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
    lines = iter(text.splitlines())

    _raise_for_startswith('QN AMZSITA', next(lines))
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

    # ignore remaining

    return data

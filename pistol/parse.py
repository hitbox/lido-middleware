from units import VALID_WEIGHT_UNITS

from .regex import config_line_re
from .regex import detail_weight_line_re
from .regex import end_line_re
from .regex import main_deck_header
from .regex import other_weight_line_re
from .regex import pistol_metadata_re
from .regex import space_run
from .regex import tape_line_re
from .regex import weight_and_unit_re

from extradata import stations

class ParsingError(Exception):
    """
    """


def _position(line):
    """
    Parse a single line of container / pallet distribution.
    """
    if not line.startswith('-'):
        raise ParsingError('line does not start with dash')
    if '\n' in line:
        raise ParsingError('line contains newline')
    # init result
    position_data = dict(
        #text_src = line,
        position = None,
        unit_load_device = None,
        destination_iata = None,
        destination_icao = None,
        weight = None,
        weight_unit = None,
        building = None,
    )
    # strip leading dash
    line = line[1:]
    # NIL or forward slash separated
    if line.endswith('.NIL'):
        position_data['position'] = line.split('.')[0]
    else:
        position, unit_load_device, destination_iata_or_icao, weight, building = line.split('/')
        position_data['position'] = position
        position_data['unit_load_device'] = unit_load_device
        # destination station
        # it can be IATA or ICAO. detect and set.
        station = destination_iata_or_icao.strip()
        postfix = stations.detect_code_type(station).lower()
        position_data['destination_' + postfix] = station
        #
        match = weight_and_unit_re.match(weight)
        if not match:
            raise ParsingError('Unable to parse weight %r' % weight)
        weightdata = match.groupdict()
        position_data['weight'] = weightdata['weight']
        position_data['weight_unit'] = weightdata['weight_unit']

        position_data['building'] = building
    # strip whitespace
    for k, v in position_data.items():
        if isinstance(v, str):
            v = v.strip()
            v = v if v else None
            position_data[k] = v
    return position_data

def _weights_and_config_data(lines_iter, color_code):
    """
    Return weights and configuration data as tuple weights_data, config_data.
    """
    # find header for weights and configuration
    maxtries = 1000
    header = ['WGT', 'WGT', 'FWD', 'CG', '%MAC', 'AFT', 'CONFIG']
    # add the color code split exactly like the lines will be
    header.extend(space_run.split(color_code))
    for tries, line in enumerate(lines_iter, start=1):
        # replace runs of spaces with a single space
        items = space_run.split(line)[:len(header)]
        if items == header:
            # found header for weights and other config info
            break
        elif tries == maxtries:
            raise ParsingError('Unable to find weights header line')
    # split on column index
    config_header_index = line.index('CONFIG  ')
    weight_lines = []
    config_lines = []
    other_weight_lines = []
    while True:
        line = next(lines_iter)
        if line.startswith('Fuel Wing Wt'):
            other_weight_lines.append(line)
            break
        weight_part = line[:config_header_index].strip()
        config_part = line[config_header_index:].strip()
        if weight_part:
            weight_lines.append(weight_part)
        if config_part:
            config_lines.append(config_part)
    # collect other weight lines until start of main deck report
    while True:
        try:
            line = next(lines_iter)
        except StopIteration:
            raise ParsingError('Unable to find main deck report line')
        if main_deck_header.match(line):
            break
        other_weight_lines.append(line)
    # parse detail weight lines
    weights_data = []
    for weight_line in weight_lines:
        match = detail_weight_line_re.match(weight_line)
        if not match:
            raise ParsingError('Unable to parse detail weight line, %r' % weight_line)
        weights_data.append(match.groupdict())
    # parse other weight lines
    for other_weight_line in other_weight_lines:
        match = other_weight_line_re.match(other_weight_line)
        if not match:
            raise ParsingError('Unable to parse other weight line, %r' % other_weight_line)
        weights_data.append(match.groupdict())
    # parse config lines
    config_data = []
    for config_line in config_lines:
        match = config_line_re.match(config_line)
        if not match:
            raise ParsingError('Unable to parse aircraft config line, %r' % config_line)
        config_data.append({k.strip(): v.strip() for k, v in match.groupdict().items()})
    # N/A -> None
    for data in weights_data + config_data:
        for key, value in data.items():
            if value == 'N/A':
                data[key] = None
    return (weights_data, config_data)

def _flight_number_and_company(s):
    """
    Split string into flight number and company tuple.
    """
    if s.startswith('ATIATN'):
        company = 'ATI'
        flightindex = 6
    else:
        flightindex = 3
        company = s[:3]
    flightnumber = s[flightindex:]
    return (flightnumber, company)

def _actual_departure_time(s):
    if not (s.isdigit() or s == 'Update'):
        raise ParsingError('Invalid actual time of departure, got %r' % s)
    # the ad_unknown1 has been observed as N/A. assume actual_departure_time
    # can be N/A too.
    if s in ('Update', 'N/A'):
        return None
    else:
        return s

def loadplan_from_lines(lines):
    """
    :param lines: list of lines excluding the newlines.
    """
    # this function takes the strategy of reading the lines in an expected
    # order, with some being optional.
    loadplan_data = dict(
        destination_iata = None,
        destination_icao = None,
        origin_iata = None,
        origin_icao = None,
    )
    lines_iter = iter(lines)

    # load planner
    line = next(lines_iter)
    if not line.startswith('LP '):
        raise ParsingError('Expected LP (load planner) line not found')
    #
    loadplan_data['load_planner'] = line[3:]
    # newlines can appear inside, what should be, the load planner line.
    maxtries = 3
    for tries, line in enumerate(lines_iter, start=1):
        if line == 'MVT':
            break
        elif tries == maxtries:
            raise ParsingError(
                    'Unable to process LP line, failed looking for MVT line.' % maxtries)
        loadplan_data['load_planner'] += line

    company_and_flight_number, rest = next(lines_iter).split('/')
    daynum1, ac_registration1, origin_icao = rest.split('.')
    flight_number, company = _flight_number_and_company(company_and_flight_number)
    loadplan_data['company'] = company
    loadplan_data['flight_number'] = flight_number
    loadplan_data['aircraft_registration'] = ac_registration1
    loadplan_data['origin_icao'] = origin_icao

    # ATD: Actual Time of Departure
    # AD(Update|\d{4})/(Update|???).<some code>.<destination station icao>
    # FL171.docx says this is an "Aircraft Registration" section.
    line = next(lines_iter)
    if not line.startswith('AD'):
        raise ParsingError('Error, expected AD')
    # omitting leading "AD" and split on forward slash
    actual_departure_time_str, rest = line[2:].split('/', maxsplit=1)
    try:
        loadplan_data['actual_departure_time'] = _actual_departure_time(actual_departure_time_str)
    except ParsingError:
        raise ParsingError('Unable to parse AD line, %r' % line)
    # the ad_unknown1 has been observed as N/A. assume actual_departure_time
    # can be N/A too.
    # ad_unknown1 is four digts, N/A or Update
    # if it is a time is is usually after actual_departure_time but can be before.
    ad_unknown1, ad_unknown2, destination_iata_or_icao = rest.split('.')
    # destination station can be IATA or ICAO. detect and set appropriately.
    station = destination_iata_or_icao.strip()
    postfix = stations.detect_code_type(station).lower()
    loadplan_data['destination_' + postfix] = station

    # this seems to be a summary of total weight and number of ulds
    line = next(lines_iter)
    if not line.startswith('PL'):
        raise ParsingError('Error, expected PL')

    # Souls on Board?
    line = next(lines_iter)
    if not line.startswith('SOB'):
        raise ParsingError('Error, expected SOB')
    loadplan_data['souls_onboard'] = line.split(' ')[1]

    # NOTOC: optional line
    line = next(lines_iter)
    if line == ' Look for NOTOC.':
        line = next(lines_iter)

    if not line.startswith('CPM'):
        raise ParsingError('Error, expected CPM')

    #  flight number, day, aircraft registration, color code
    line = next(lines_iter)
    flight2, rest = line.split('/')
    if company_and_flight_number != flight2:
        raise ParsingError('flight numbers differ')
    daynum2, ac_registration2, color_code = rest.split('.')
    if ac_registration1 != ac_registration2:
        raise ParsingError('aircraft registrations differ')
    if daynum1 != daynum2:
        raise ParsingError('day numbers differ')
    loadplan_data['day'] = daynum2
    loadplan_data['color_code'] = color_code

    # list of positions and weights
    loadplan_data['positions'] = []
    while True:
        line = next(lines_iter)
        if not line.startswith('-'):
            break
        position_data = _position(line)
        loadplan_data['positions'].append(position_data)

    # all weights unit...
    s = 'SI ALL WGT ARE '
    if not line.startswith(s):
        raise ParsingError('Expected %r line' % s)
    # ...last two characters
    all_weights_unit = line[-2:]
    if all_weights_unit not in VALID_WEIGHT_UNITS:
        raise ParsingError('Invalid weight units, got %s' % all_weights_unit)
    loadplan_data['all_weights_unit'] = all_weights_unit

    # find tape line
    maxtries = 5
    for tries, line in enumerate(lines_iter, start=1):
        if tape_line_re.match(line):
            break
        elif tries == maxtries:
            raise ParsingError('Unable to find tape line after %s attempts' % maxtries)

    # pistol and print meta data
    line = next(lines_iter)
    match = pistol_metadata_re.match(line)
    if not match:
        raise ParsingError('Unable to parse pistol metadata line %r' % line)
    # pistol_version, computer, print_time_local, print_time_gmt
    loadplan_data.update(match.groupdict())

    # redundant info of flight, tail and station
    line = next(lines_iter)
    if not line.startswith('Load Plan '):
        raise ParsingError('Expected "Load Plan " line')

    weights_data, config_data = _weights_and_config_data(lines_iter, color_code)
    loadplan_data['weights'] = weights_data
    loadplan_data['aircraft_configurations'] = config_data

    # find the end
    maxtries = 1000
    for tries, line in enumerate(lines_iter, start=1):
        if end_line_re.match(line):
            # good, we are done.
            break
        elif tries == maxtries:
            raise ParsingError('Unable to find end line after %s attempts' % maxtries)

    return loadplan_data

def loadplan_from_text(text):
    """
    Pull data out of pstl text message, prepared for conversion to data types
    by schema.
    """
    return loadplan_from_lines(text.splitlines())

def loadplan_from_message(message):
    return loadplan_from_text(message.text)

def main(argv=None):
    """
    Parse PSTL weight and balance message from file.
    """
    import argparse
    import string

    from pathlib import Path

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        'file',
        nargs = '+',
        type = Path,
        help = 'PSTL text file as dumped from email')
    parser.add_argument(
        '--strip-email-wrapper',
        action = 'store_true',
        help = 'Strip the metadata about what email the text was dumped'
               ' from--first and last three lines.')
    parser.add_argument(
        '--only-ascii',
        action = 'store_true',
        help = 'Examine only ascii characters.')
    parser.add_argument(
        '--write-errors',
        type = Path,
        metavar = 'DIR',
        help = 'Write errors to files in given directory. Must exist and not be'
               ' in the input files dir.')
    args = parser.parse_args(argv)

    if args.write_errors:
        if not args.write_errors.exists():
            parser.error('error output must exist')
        for path in args.file:
            if path.parent == args.write_errors:
                parser.error('error output must not be same dir as any file')

    error_bucket = []
    for path in args.file:
        with open(path) as f:
            text = f.read()
            if args.strip_email_wrapper:
                lines = text.splitlines()
                text = '\n'.join(lines[3:-3])
            if args.only_ascii:
                text = ''.join(c for c in text if c in string.printable)
            try:
                loadplan_from_text(text)
            except Exception as e:
                error_bucket.append((path, e, text))

    if error_bucket:
        if args.write_errors:
            for path, e, text in error_bucket:
                msg = str(e)
                outpath = args.write_errors / path.name
                with open(outpath, 'w') as outf:
                    outf.write('from: ' + str(path) + '\n')
                    outf.write(msg + '\n')
                    outf.write(text)
        else:
            for path, e, text in error_bucket:
                print(path)
                print(text)
                print(e)
        print('%s errors' % len(error_bucket))

if __name__ == '__main__':
    main()

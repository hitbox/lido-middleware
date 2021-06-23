"""
Extract string data from Pistol message. Nothing but None and strings should
come out of here.
"""
from run.exceptions import ExtractError

from .regex import ad_line_re
from .regex import config_line_re
from .regex import dense_line_re1
from .regex import dense_line_re2
from .regex import detail_weight_line_re
from .regex import end_line_re
from .regex import main_deck_header
from .regex import other_weight_line_re
from .regex import pistol_metadata_re
from .regex import position_line_nil_re
from .regex import position_line_re
from .regex import si_line_re
from .regex import souls_onboard_re
from .regex import space_run
from .regex import tape_line_re

class PistolExtractError(ExtractError):
    pass


def _position(line):
    """
    Parse a single line of container / pallet distribution.
    """
    for line_re in [position_line_nil_re, position_line_re]:
        match = line_re.match(line)
        if match:
            return match.groupdict()
    else:
        raise PistolExtractError('error matching position line %r' % line)

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
            raise PistolExtractError('Unable to find weights header line')
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
        if not (weight_part or config_part):
            raise PistolExtractError(
                'Unable to parse weight or config parts from line %r' % line)
        if weight_part:
            weight_lines.append(weight_part)
        if config_part:
            config_lines.append(config_part)
    # collect other weight lines until start of main deck report
    for line in lines_iter:
        if main_deck_header.match(line):
            break
        other_weight_lines.append(line)
    # pull detail weight lines data
    weights_data = []
    for weight_line in weight_lines:
        match = detail_weight_line_re.match(weight_line)
        if not match:
            raise PistolExtractError('Unable to parse detail weight line, %r' % weight_line)
        weights_data.append(match.groupdict())
    # pull other weight lines data
    for other_weight_line in other_weight_lines:
        match = other_weight_line_re.match(other_weight_line)
        if not match:
            raise PistolExtractError('Unable to parse other weight line, %r' % other_weight_line)
        weights_data.append(match.groupdict())
    # pull config lines data
    config_data = []
    for config_line in config_lines:
        match = config_line_re.match(config_line)
        if not match:
            raise PistolExtractError('Unable to parse aircraft config line, %r' % config_line)
        config_data.append({k.strip(): v.strip() for k, v in match.groupdict().items()})
    return (weights_data, config_data)

def loadplan_from_lines(lines):
    """
    :param lines: list of lines excluding the newlines.
    """
    # this function takes the strategy of reading the lines in an expected
    # order, with some being optional.
    loadplan_data = dict()
    lines_iter = iter(lines)

    # extract load planner
    line = next(lines_iter)
    if not line.startswith('LP '):
        raise PistolExtractError('Expected LP (load planner) line not found. %r' % line)
    loadplan_data['load_planner'] = line[3:]

    # newlines can appear inside, what should be, the load planner line.
    maxtries = 3
    for tries, line in enumerate(lines_iter, start=1):
        if line == 'MVT':
            break
        elif tries == maxtries:
            raise PistolExtractError(
                'Unable to process LP line, failed looking for MVT line.'
                % maxtries)
        loadplan_data['load_planner'] += line

    line = next(lines_iter)
    match = dense_line_re1.match(line)
    if not match:
        raise PistolExtractError('no match first dense line %r' % line)
    loadplan_data.update(match.groupdict())

    # ATD: Actual Time of Departure
    # FL171.docx says this is an "Aircraft Registration" section.
    line = next(lines_iter)
    match = ad_line_re.match(line)
    if not match:
        raise PistolExtractError('unmatched AD line %r' % line)
    loadplan_data.update(match.groupdict())

    # this seems to be a summary of total weight and number of ulds
    line = next(lines_iter)
    if not line.startswith('PL'):
        raise PistolExtractError('Error, expected PL')

    # Souls on Board
    line = next(lines_iter)
    match = souls_onboard_re.match(line)
    if not match:
        raise PistolExtractError('unmatched SOB line %r' % line)
    loadplan_data.update(match.groupdict())

    # NOTOC: optional line
    line = next(lines_iter)
    if line == ' Look for NOTOC.':
        line = next(lines_iter)

    if not line.startswith('CPM'):
        raise PistolExtractError('Error, expected CPM')

    #  flight number, day, aircraft registration, color code
    line = next(lines_iter)
    match = dense_line_re2.match(line)
    if not match:
        raise PistolExtractError('no match second dense line %r' % line)
    loadplan_data.update(match.groupdict())

    # skip past the list of positions and weights
    for line in lines_iter:
        if not line.startswith('-'):
            break

    # using line from loop above
    match = si_line_re.match(line)
    if not match:
        raise PistolExtractError('no match SI line %r' % line)
    loadplan_data.update(match.groupdict())

    # find tape line
    maxtries = 5
    for tries, line in enumerate(lines_iter, start=1):
        if tape_line_re.match(line):
            break
        elif tries == maxtries:
            raise PistolExtractError('Unable to find tape line after %s attempts' % maxtries)

    # pistol and print meta data
    line = next(lines_iter)
    match = pistol_metadata_re.match(line)
    if not match:
        raise PistolExtractError('Unable to parse pistol metadata line %r' % line)
    # pistol_version, computer, print_time_local, print_time_gmt
    loadplan_data.update(match.groupdict())

    # redundant info of flight, tail and station
    line = next(lines_iter)
    if not line.startswith('Load Plan '):
        raise PistolExtractError('Expected "Load Plan " line')

    weights_data, config_data = _weights_and_config_data(lines_iter, loadplan_data['color_code'])
    loadplan_data['weights'] = weights_data
    loadplan_data['aircraft_configurations'] = config_data

    # find the end
    maxtries = 1000
    for tries, line in enumerate(lines_iter, start=1):
        if end_line_re.match(line):
            # good, we are done.
            break
        elif tries == maxtries:
            raise PistolExtractError('Unable to find end line after %s attempts' % maxtries)

    return loadplan_data

def loadplan_from_text(text):
    """
    Pull data out of pistol text message, prepared for conversion to data types
    by schema.
    """
    return loadplan_from_lines(text.splitlines())

def loadplan_from_message(message):
    """
    Loadplan data from email message. Adds message data too.
    """
    #text = message.attachments[0].payload.decode()
    loadplan_data = loadplan_from_text(message.text)
    loadplan_data['message_to'] = message.to
    return loadplan_data

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

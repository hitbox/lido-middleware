from run.exceptions import ExtractError

from .regex import dense_data_line_re
from .regex import positions_header_re
from .regex import si_load_re
from .regex import si_load_uld_count_re

from schema import PRINT_DATETIME_FORMAT

class SableExtractError(ExtractError):
    pass


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
        raise SableExtractError(
            'Unable to find and parse dense data line, %r' % line)

    # SI LOAD information line
    line = next(lines)
    match = si_load_re.match(line)
    if not match:
        raise SableExtractError(
            'Unable to parse SI LOAD information line, %r' % line)
    sable_data.update(match.groupdict())

    # optional uld count parse
    match = si_load_uld_count_re.match(line)
    if match:
        sable_data.update(match.groupdict())

    # find position data header line
    for line in lines:
        match = positions_header_re.match(line)
        if match:
            break
    else:
        raise SableExtractError('Positions data header line not found.')

    # positions rows
    fieldnames = [group.strip() for group in match.groups()]
    spans = []
    for index, group in enumerate(match.groups(), start=1):
        spans.append(match.span(index))
    sable_data['positions'] = positions = []
    for line in lines:
        if line.strip() == '':
            break
        data = {fieldname: line[start:end].strip() for (start, end), fieldname in zip(spans, fieldnames)}
        positions.append(data)

    return sable_data

def loadplan_from_message(message):
    """
    Sable data from email message, partially deserialized.
    """
    # NOTE: some of these are failing and could fallback on the message subject
    # line for the company. maybe other things too.
    first_attached = message.attachments[0]
    text = first_attached.payload.decode('utf8', 'ignore')
    data = from_text(text)
    data['message_date'] = message.date.strftime(PRINT_DATETIME_FORMAT)
    data['message_to'] = message.to
    data['message_from'] = message.from_
    return data

def main(argv=None):
    """
    """
    import argparse
    import pickle

    parser = argparse.ArgumentParser()
    parser.add_argument('--source-pickle')
    parser.add_argument('--index', type=int)
    args = parser.parse_args(argv)

    with open(args.source_pickle, 'rb') as fp:
        messages = pickle.load(fp)

    messages = [msg for msg in messages
        if msg.subject.startswith('LDM')
        and msg.from_ in ('avibar@dhl.com', 'amazon-sable@amazon-wb.com')]
    result = loadplan_from_message(messages[args.index])

if __name__ == '__main__':
    main()

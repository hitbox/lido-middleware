def parse_wabformat(file):
    """
    Parse the human readable WABFORMAT.txt file for the message table that
    describes the format of a LIDO message.

    This function builds a dictionary that makes plucking the values FROM a
    LIDO message.
    """
    # hasty parse for the WABFORMAT.txt file.
    text = file.read()
    lines = iter(text.splitlines())

    while True:
        line = next(lines)
        if line == '#message_table':
            break

    header = [s.strip() for s in next(lines).split('|') if s.strip()]
    # ignore next line
    next(lines)

    data = []
    for line in lines:
        if not line:
            break
        row = [s.strip() for s in line.split('|') if s.strip()]
        data.append(dict(zip(header, row)))

    indexed = {}
    start = 0
    for i, row in enumerate(data):
        name = row['Field Description']
        length = int(row['Length'])
        indexed[name] = {'start': start, 'length': length}
        start += length

    return indexed

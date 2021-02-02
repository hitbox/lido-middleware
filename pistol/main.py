import argparse
import string

from pathlib import Path

import pistol.extract
import pistol.schema

def main(argv=None):
    """
    Parse PSTL weight and balance message from file.
    """
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
                loadplan_data = pistol.extract.loadplan_from_text(text)
                loadplan = pistol.schema.LoadPlanSchema().load(loadplan_data)
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

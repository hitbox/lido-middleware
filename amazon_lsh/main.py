import argparse
import pickle
import traceback

from pathlib import Path

from .extract import AmazonLSHExtractError
from .extract import loadplan_from_message
from .schema import LoadPlanSchema

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pickle', nargs='+', help='Load messages from pickle file')
    parser.add_argument('--silent', action='store_true')
    args = parser.parse_args(argv)

    # this will remain loosey goosey to meet my needs

    for fn in map(Path, args.pickle):
        with open(fn, 'rb') as fp:
            messages = pickle.load(fp)
            for msg in messages:
                try:
                    lp = loadplan_from_message(msg)
                except AmazonLSHExtractError:
                    if not args.silent:
                        print(fn)
                        print(msg.subject)
                        traceback.print_exc()
                else:
                    data = LoadPlanSchema().load(lp)
                    print_time_gmt = data['print_time_gmt']
                    if (print_time_gmt.hour == 0
                            and print_time_gmt.minute == 0
                            and print_time_gmt.second == 0):
                        print(f'Subject: {msg.subject}')
                        print(f'Body:\n{msg.text}')
                        print('\n\n')

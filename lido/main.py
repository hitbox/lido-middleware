import argparse

from pathlib import Path

import pistol.parse

from pistol.schema import LoadPlanSchema

from . import LIDOWeightBalanceMessage
from . import wabformat

def main(argv=None):
    """
    Print LIDO weight/balance message string and the extracted values from it
    based on the table in WABFORMAT.txt.
    """
    parser = argparse.ArgumentParser(description=main.__doc__, prog='lido')
    parser.add_argument(
        '-f', '--file',
        help='Text file with pistol message text in it.')
    args = parser.parse_args(argv)

    path = Path(__file__).parent / 'WABFORMAT.txt'
    with open(path) as wabformat_file:
        index = wabformat.parse_wabformat(wabformat_file)

    with open(args.file) as file:
        data = pistol.parse.loadplan_from_text(file.read())
        loadplan = LoadPlanSchema().load(data)
        wbmsg = str(LIDOWeightBalanceMessage(loadplan))
        print(repr(wbmsg))
        for name, idx in index.items():
            start = idx['start']
            length = idx['length']
            portion = wbmsg[start:start+length]
            print(name, repr(portion), len(portion), length)

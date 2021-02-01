import argparse
import pickle
import sys

from pathlib import Path

from jinja2 import Template

from . import parse
from . import schema

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('-f', '--file', nargs='+', type=argparse.FileType())
    parser.add_argument('-p', '--pickle', nargs='+')
    parser.add_argument('--html', action='store_true')
    args = parser.parse_args(argv)

    if args.file and args.pickle:
        parser.error('only one operation may be used at a time')

    loadplanschema = schema.LoadPlanSchema()

    loadplans = []
    if args.file:
        for file in args.file:
            text = file.read()
            loadplan_data = parse.parse_from_text(text)
            loadplan = loadplanschema.load(loadplan_data)
            loadplans.append(loadplan)
    elif args.pickle:
        for pckl in args.pickle:
            with open(pckl, 'rb') as pcklfile:
                message = pickle.load(pcklfile)
                text = message.attachments[0].payload.decode('utf8')
                loadplan_data = parse.parse_from_text(text)
                loadplan = loadplanschema.load(loadplan_data)
                loadplans.append(loadplan)

    if args.html:
        path = Path(__file__).parent / 'loadplan_table.html'
        with open(path) as template_file:
            template = Template(template_file.read())
            for loadplan in loadplans:
                html = template.render(loadplan=loadplan)
                print(html)

if __name__ == '__main__':
    sys.exit(main())

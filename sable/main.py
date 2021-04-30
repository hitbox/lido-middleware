import argparse
import email
import pickle

from pathlib import Path

from jinja2 import Template

from . import extract
from . import schema

def main(argv=None):
    """
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('-f', '--file', nargs='+', type=argparse.FileType())
    parser.add_argument('-p', '--pickle', nargs='+')
    parser.add_argument('-e', '--eml', nargs='+', help='email.message_from_file')
    parser.add_argument('--html', default='-', nargs='?', type=argparse.FileType('w'))
    args = parser.parse_args(argv)

    if args.file and args.pickle:
        parser.error('only one operation may be used at a time')

    loadplanschema = schema.LoadPlanSchema()

    loadplans = []
    if args.file:
        for file in args.file:
            text = file.read()
            loadplan_data = extract.from_text(text)
            loadplan = loadplanschema.load(loadplan_data)
            loadplans.append(loadplan)
    elif args.pickle:
        for pckl in args.pickle:
            with open(pckl, 'rb') as pcklfile:
                message = pickle.load(pcklfile)
                text = message.attachments[0].payload.decode('utf8')
                loadplan_data = extract.from_text(text)
                loadplan = loadplanschema.load(loadplan_data)
                loadplans.append(loadplan)
    elif args.eml:
        for fn in args.eml:
            with open(fn, 'rb') as fp:
                message = email.message_from_bytes(fp.read())
                for part in message.walk():
                    print(fn)
                    print(part.get_content_type())
                    print(part.get_content_charset())
                    #if part.get_content_type() == 'text/plain':
                    #    print(fn)
                    #    print(part.get_payload())
                    #print([item for item in part.items() if 'name' in item[0].lower()])
                    if part.get_content_disposition() == 'attachment':
                        pass

    if args.html:
        path = Path(__file__).parent / 'loadplan_table.html'
        with open(path) as template_file:
            template = Template(template_file.read())
            for loadplan in loadplans:
                html = template.render(loadplan=loadplan)
                print(html, file=args.html)

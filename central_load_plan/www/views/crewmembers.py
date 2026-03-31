import csv
import datetime
import glob
import os
import re

from pprint import pprint

import click
import sqlalchemy as sa

from sqlalchemy.orm import Session

from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markupsafe import Markup
from sqlalchemy.orm import Session
from flask_login import login_required
from flask_login import current_user

import central_load_plan.config
import central_load_plan.crewmember

from central_load_plan.constants import AIRLINE_CODES
from central_load_plan.engine import get_lsyrept_engine
from central_load_plan.flight_plan_parser import FlightPlanParser
from central_load_plan.models.lsyrept import ChainItemDaily
from central_load_plan.models.lsyrept import CrewMember
from central_load_plan.models.lsyrept import Duty
from central_load_plan.models.lsyrept import ItemDaily
from central_load_plan.models.lsyrept import LSYBase
from central_load_plan.models.lsyrept import NonCrewMember
from central_load_plan.models.lsyrept import RemarkOfEvent
from central_load_plan.schema import ChainItemDailySchema
from central_load_plan.schema import CrewMemberSchema
from central_load_plan.schema import DutySchema
from central_load_plan.schema import EFFArchivePathSchema
from central_load_plan.schema import ItemDailySchema
from central_load_plan.schema import NonCrewMemberSchema
from central_load_plan.schema import OperationalFlightPlanSchema
from central_load_plan.schema import RemarkOfEventSchema
from central_load_plan.schema import lsyrept_model_schemas
from central_load_plan.www import app
from central_load_plan.www.form import CrewmemberArgsForm
from central_load_plan.www.form import EFFArchiveFilterForm
from central_load_plan.www.html import render_object
from central_load_plan.www.extension import login_manager

crewmember_bp = Blueprint('crewmember', __name__)

class CriteriaDict:

    def __init__(self, dict_):
        self.dict_ = dict_

    def __call__(self, data):
        return all(data[key] == value for key, value in self.dict_.items() if key in data)


@crewmember_bp.before_request
def require_login():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()


@crewmember_bp.route('/')
def index():
    return redirect(url_for('.query'))

@crewmember_bp.route(
    '/from-data'
    '/<airline_code>'
    '/<date:archive_date>'
    '/<origin>'
    '/<destination>'
    '/<time:timestamp>'
)
def from_data(airline_code, archive_date, origin, destination, timestamp):
    """
    Parse EFF XML file for data from path data or similar.
    """
    criteria = locals()

    eff_archive = current_app.config.get('EFF_ARCHIVE')

    ofp_schema = OperationalFlightPlanSchema()

    substitutions = {
        'airline_code': airline_code,
        'date': archive_date,
    }

    flight_plan_parser = FlightPlanParser()

    for path_data in eff_archive.iter_files(substitutions):
        # all the criteria keys from arguments that match path data
        if all(criteria[key] == value for key, value in criteria.items() if key in path_data):
            ofp_strings = flight_plan_parser.parse_path(path_data['path'])
            ofp_data = ofp_schema.load(ofp_strings)
            engine = get_lsyrept_engine(airline_code)
            with Session(engine) as session:
                ofp_strings['crewmembers'] = list(central_load_plan.crewmember.fromdata(session, ofp_data))
            ofp_data = ofp_schema.load(ofp_strings)
            result = {
                'ofp_data': ofp_schema.dump(ofp_data),
                'path_data': eff_archive.parser.schema.dump(path_data),
            }
            return jsonify(result)

@crewmember_bp.route('/query', methods=['GET', 'POST'])
def query():
    """
    Query database for crew members, jump seats and dead heads.
    """
    result = None
    form = CrewmemberArgsForm(formdata = request.form or request.args)

    eff_archive_form = EFFArchiveFilterForm(request.args)

    if request.method == 'POST' and form.validate():
        # there doesn't seem to be support for html datetime field, it just
        # comes out as a text input
        # so we combine them here
        flight_data = dict(
            airline_iata_code = form.airline_iata_code.data,
            flight_origin_date = form.flight_origin_date.data,
            flight_number = form.flight_number.data,
            origin_iata = form.origin_iata.data,
            scheduled_departure_time = datetime.datetime.combine(
                form.scheduled_departure_date.data,
                form.scheduled_departure_time.data,
            ),
        )
        return jsonify(flight_data)
        engine = get_lsyrept_engine(form.airline_iata_code.data)
        with Session(engine) as session:
            result = central_load_plan.crewmember.fromdata(session, flight_data)

    eff_archive = current_app.config.get('EFF_ARCHIVE')
    eff_path_parser = current_app.config.get('EFF_PATH_PARSER')
    eff_archive_path_schema = EFFArchivePathSchema()

    substitutions = {
        'airline_code': eff_archive_form.airline_iata_code.data,
        'date': eff_archive_form.archive_date.data,
    }
    eff_paths = list(eff_archive.iter_files(substitutions))
    #eff_paths = map(os.path.normpath, eff_paths)
    #eff_paths = (eff_data for eff_data in map(eff_path_parser, eff_paths) if eff_data)
    #eff_paths = [eff_archive_path_schema.load(eff_data) for eff_data in eff_paths]

    interesting_data = current_app.config.get('CREWMEMBERS_INTERESTING_DATA', [])
    context = {
        'form': form,
        'interesting_data': interesting_data,
        'result': result,
        'eff_archive_form': eff_archive_form,
        'eff_paths': eff_paths,
        'substitutions': substitutions,
    }
    return render_template('crewmember/query.html', **context)

def get_lsyrept_schema(model):
    for schema_class in lsyrept_schemas:
        if schema_class.Meta.model == model:
            return schema_class

crewmember_bp.cli.help = (
    'Command-line commands for examining queries related to finding crew'
    ' members for given OFPs.'
)

@crewmember_bp.cli.command('dump')
@click.option('--print-only', is_flag=True)
def dump(print_only):
    """
    Dump external database tables for all airlines.
    """
    for airlinecode in AIRLINE_CODES:
        for model in LSYBase.__subclasses__():
            filename = f'{airlinecode}_{model.__name__}.csv'
            schema_class = lsyrept_model_schemas[model]
            schema = schema_class()
            query = sa.select(model)
            fieldnames = [c.name for c in query.selected_columns]
            try:
                engine = get_lsyrept_engine(airlinecode)
            except:
                continue
            with Session(engine) as session:
                rows = session.execute(query).mappings()
                if print_only:
                    print(filename)
                    for row in rows:
                        print(row)
                else:
                    with open(filename, 'w', newline='') as output_file:
                        writer = csv.DictWriter(output_file, fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)

@crewmember_bp.cli.command('load')
@click.argument('dump_path')
@click.option('--filename-parser', default=r'(?P<airline_code>8C|GB)_(?P<model_name>ChainItemDaily|CrewMember|Duty|ItemDaily|NonCrewMember|RemarkOfEvent)\.csv')
def load(dump_path, filename_parser):
    filename_parser = re.compile(filename_parser)
    for csv_fn in os.listdir(dump_path):
        match = filename_parser.match(csv_fn)
        if not match:
            raise ValueError(f'{csv_fn} did not match regex')
        fn_data = match.groupdict()
        airline_code = fn_data['airline_code']
        engine = get_lsyrept_engine(airline_code)
        LSYBase.metadata.create_all(engine)
        print(engine)
        with Session(engine) as session:
            model_name = fn_data['model_name']
            model = eval(model_name)
            print(model)
            schema_class = lsyrept_model_schemas[model]
            schema = schema_class(session=session)
            schema.context = {'session': session}
            csv_path = os.path.join(dump_path, csv_fn)
            print(csv_path)
            with open(csv_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file, fieldnames=schema.fields.keys())
                for row in reader:
                    instance = schema.load(row)
                    session.add(instance)
            session.commit()

@crewmember_bp.cli.command('fromdata')
@click.argument('airline_code')
@click.argument('origin_iata')
@click.argument('origin_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.argument('flight_number', type=click.INT) # usually LSYREPT uses integer
@click.argument('scheduled_departure_time', type=click.DateTime(formats=['%H:%M']))
def fromdata(airline_code, origin_iata, origin_date, flight_number, scheduled_departure_time):
    # Keep only the datetime parts we need.
    origin_date = origin_date.date()
    scheduled_departure_time = scheduled_departure_time.time()
    engine = get_lsyrept_engine(airline_code)
    with Session(engine) as session:
        scheduled_departure_time = datetime.datetime.combine(origin_date, scheduled_departure_time)
        flight_data = {
            'flight_number': flight_number,
            'flight_origin_date': origin_date,
            'airline_iata_code': airline_code,
            'origin_iata': origin_iata,
            'scheduled_departure_time': scheduled_departure_time,
        }
        for whatever in central_load_plan.crewmember.fromdata(session, flight_data):
            print(whatever)

@crewmember_bp.cli.command('from_path')
@click.argument('airline_code')
@click.argument('archive_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.argument('origin')
@click.argument('destination')
@click.argument('filename_time', type=click.DateTime(formats=['%H:%M:%S']))
def from_path(airline_code, archive_date, origin, destination, filename_time):
    # Keep only the datetime parts we need.
    archive_date = archive_date.date()
    filename_time = filename_time.time()

    criteria = {
        'airline_code': airline_code,
        'archive_date': archive_date,
        'origin': origin,
        'destination': destination,
        'time': filename_time,
    }
    print(f'{criteria=}')
    matcher = CriteriaDict(criteria)

    eff_archive_path_schema = EFFArchivePathSchema()
    substitutions = {
        'airline_code': airline_code,
        'date': archive_date,
    }
    eff_path_parser = current_app.config.get('EFF_PATH_PARSER')

    ofp_schema = OperationalFlightPlanSchema()
    for path in eff_archive_paths.paths(substitutions=substitutions):
        eff_data = eff_path_parser(path)
        eff_data = eff_archive_path_schema.load(eff_data)
        # all the criteria keys from arguments that match path data
        if matcher(eff_data):
            print(f'MATCH: {path=}')
            ofp_data = ofp_schema.load(ofp_strings)

            engine = get_lsyrept_engine(airline_code)
            with Session(engine) as session:
                print(list(central_load_plan.crewmember.fromdata(session, ofp_data)))

@crewmember_bp.cli.command('from_archive')
@click.argument('')
def from_archive(airline_code, archive_date):
    # Added cli command because breakpoints work much better here.
    # Keep only the datetime parts we need.
    archive_date = archive_date.date()

    criteria = {
        'airline_code': airline_code,
        'archive_date': archive_date,
    }
    matcher = CriteriaDict(criteria)

    eff_archive = current_app.config.get('EFF_ARCHIVE')
    eff_archive_path_schema = EFFArchivePathSchema()
    substitutions = {
        'airline_code': airline_code,
        'date': archive_date,
    }
    eff_path_parser = current_app.config.get('EFF_PATH_PARSER')

    ofp_schema = OperationalFlightPlanSchema()
    for path in eff_archive.iter_files(substitutions):
        eff_data = eff_path_parser(path)
        eff_data = eff_archive_path_schema.load(eff_data)
        # all the criteria keys from arguments that match path data
        if matcher(eff_data):
            print(f'MATCH: {path=}')
            #ofp_strings = central_load_plan.pluck.from_path(path)
            ofp_data = ofp_schema.load(ofp_strings)

            # TODO
            # - put all this song and dance into a function or something to
            #   document and formalize it.

            engine = get_lsyrept_engine(airline_code)
            with Session(engine) as session:
                print(list(central_load_plan.crewmember.fromdata(session, ofp_data)))

@crewmember_bp.cli.command('load_archive')
def load_archive():
    eff_archive_parser = current_app.config.get('EFF_ARCHIVE_PARSER')

    eff_path_parser = current_app.config.get('EFF_PATH_PARSER')

    ofp_schema = OperationalFlightPlanSchema()

    for fn in glob.iglob(current_app.config.get('EFF_ARCHIVE_RECURSIVE_GLOB'), recursive=True):
        if os.path.isfile(fn):
            fn_data = eff_archive_parser(fn)
            eff_data = eff_path_parser(fn)
            eff_data = eff_archive_path_schema.load(eff_data)

    return

    eff_archive = current_app.config.get('EFF_ARCHIVE')
    eff_archive_path_schema = EFFArchivePathSchema()
    substitutions = {
        'airline_code': airline_code,
        'date': archive_date,
    }

    for path in eff_archive.iter_files(substitutions):
        # all the criteria keys from arguments that match path data
        if matcher(eff_data):
            print(f'MATCH: {path=}')
            ofp_strings = central_load_plan.pluck.from_path(path)
            ofp_data = ofp_schema.load(ofp_strings)

            # TODO
            # - put all this song and dance into a function or something to
            #   document and formalize it.

            engine = get_lsyrept_engine(airline_code)
            with Session(engine) as session:
                print(list(central_load_plan.crewmember.fromdata(session, ofp_data)))

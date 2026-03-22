import csv
import datetime
import os

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

import central_load_plan.config
import central_load_plan.pluck
import central_load_plan.crewmember

from central_load_plan.engine import get_lsyrept_engine
from central_load_plan.constants import AIRLINE_CODES
from central_load_plan.models.lsyrept import ChainItemDaily
from central_load_plan.models.lsyrept import CrewMember
from central_load_plan.models.lsyrept import Duty
from central_load_plan.models.lsyrept import ItemDaily
from central_load_plan.models.lsyrept import LSYBase
from central_load_plan.models.lsyrept import NonCrewMember
from central_load_plan.models.lsyrept import RemarkOfEvent
from central_load_plan.schema import EFFArchivePathSchema
from central_load_plan.schema import OperationalFlightPlanSchema
from central_load_plan.www import app
from central_load_plan.www.form import CrewmemberArgsForm
from central_load_plan.www.form import EFFArchiveFilterForm
from central_load_plan.www.html import render_object

crewmember_bp = Blueprint('crewmember', __name__)

@crewmember_bp.route('/')
def index():
    return redirect(url_for('.query'))

@crewmember_bp.route(
    '/from-data/<airline_code>'
    '/<date:archive_date>'
    '/<origin>'
    '/<destination>'
    '/<time:time>'
)
def from_data(airline_code, archive_date, origin, destination, time):
    """
    Parse EFF XML file for data from path data or similar.
    """
    criteria = locals()

    eff_archive_paths = current_app.config.get('EFF_ARCHIVE_PATHS')
    eff_path_parser = current_app.config.get('EFF_PATH_PARSER')
    eff_archive_path_schema = EFFArchivePathSchema()

    substitutions = {
        'airline_code': airline_code,
        'date': archive_date,
    }
    for path in eff_archive_paths.paths(substitutions=substitutions):
        data = eff_path_parser(path)
        # all the criteria keys from arguments that match path data
        if all(criteria[key] == value for key, value in criteria.items() if key in data):
            ofp_schema = OperationalFlightPlanSchema()
            ofp_strings = central_load_plan.pluck.from_path(data['path'])
            ofp_data = ofp_schema.load(ofp_strings)
            # TODO: add crew members here.
            # Let the browser show a nice UI for JSON.
            return jsonify(ofp_schema.dump(ofp_data))

    return str(locals())

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
        engine = get_lsyrept_engine(form.airline_iata_code.data)
        with Session(engine) as session:
            result = central_load_plan.crewmember.fromdata(session, flight_data)

    eff_archive_paths = current_app.config.get('EFF_ARCHIVE_PATHS')
    eff_path_parser = current_app.config.get('EFF_PATH_PARSER')
    eff_archive_path_schema = EFFArchivePathSchema()

    substitutions = {
        'airline_code': eff_archive_form.airline_iata_code.data,
        'date': eff_archive_form.archive_date.data,
    }
    eff_paths = eff_archive_paths.paths(substitutions=substitutions)
    eff_paths = map(os.path.normpath, eff_paths)
    eff_paths = (eff_data for eff_data in map(eff_path_parser, eff_paths) if eff_data)
    eff_paths = [eff_archive_path_schema.load(eff_data) for eff_data in eff_paths]

    interesting_data = current_app.config.get('CREWMEMBERS_INTERESTING_DATA', [])
    context = {
        'form': form,
        'interesting_data': interesting_data,
        'result': result,
        'eff_archive_paths': eff_archive_paths,
        'eff_archive_form': eff_archive_form,
        'eff_paths': eff_paths,
        'substitutions': substitutions,
    }
    return render_template('crewmember/query.html', **context)

@crewmember_bp.cli.command('dump')
def dump():
    """
    Dump external database tables for all airlines.
    """
    for airlinecode in AIRLINE_CODES:
        engine = get_lsyrept_engine(airlinecode)
        with Session(engine) as session:
            for model in LSYBase.__subclasses__():
                query = sa.select(model)
                fieldnames = [c.name for c in query.all_selected_columns]
                rows = session.execute(query).mappings()
                filename = f'{airlinecode}_{model.__name__}.csv'
                with open(filename, 'w', newline='') as output_file:
                    writer = csv.DictWriter(output_file, fieldnames)
                    writer.writerows(rows)

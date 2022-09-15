import datetime

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from wtforms import DateField
from wtforms import DateTimeField
from wtforms import Form
from wtforms import IntegerField
from wtforms import RadioField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import TimeField

import central_load_plan.config
import central_load_plan.crewmember

from .. import app

CONFIG_PREFIX = f'{app.CONFIG_PREFIX}_CREWMEMBERS'

crewmember_bp = Blueprint('crewmember', __name__)

INTERESTING_DATA = [
    (
        'Incident 31169: Missing dead head',
        dict(
            airline_iata_code = 'GB',
            flight_origin_date = '2022-08-31',
            flight_number = 445,
            origin_iata = 'SJU',
            scheduled_departure_date = '2022-08-31',
            scheduled_departure_time = '01:30',
        ),
    ),
    (
        'Incident 31846: No crew',
        dict(
            airline_iata_code = 'GB',
            flight_origin_date = '2022-09-09',
            flight_number = 3171,
            origin_iata = 'SBD',
            scheduled_departure_date = '2022-09-09',
            scheduled_departure_time = '04:45',
        ),
    ),
]

EXAMPLE_RESULT = central_load_plan.crewmember.CrewMemberResult(
    crewmembers = [
        dict(
            last_name = 'LASTNAME1',
            first_name = 'FIRSTNAME1',
            employee_number = 'EE1',
            seat = 'PIC',
            seat_order = 0,
            source = 'example',
        ),
        dict(
            last_name = 'LASTNAME2',
            first_name = 'FIRSTNAME2',
            employee_number = 'EE2',
            seat = 'SIC',
            seat_order = 1,
            source = 'example',
        ),
        dict(
            last_name = 'LASTNAME3',
            first_name = 'FIRSTNAME3',
            employee_number = 'EE3',
            seat = 'ACM',
            seat_order = 999,
            source = 'example',
        ),
    ],
    query = None,
    data = dict(
        airline_iata_code = 'AA',
        flight_origin_date = datetime.date(1970,1,1),
        flight_number = 123,
        origin_iata = 'XYZ',
        scheduled_departure_time = datetime.datetime(1970,1,1,1,2,3),
    ),
    engine = None,
)

class CrewmemberArgsForm(Form):
    """
    Form for arguments like what is scraped from XML.
    """

    airline_iata_code = RadioField('Airline IATA Code', choices=['GB', '8C'])
    flight_origin_date = DateField('Flight Origin Date')
    flight_number = IntegerField('Flight Number')
    origin_iata = StringField('Origin IATA')
    scheduled_departure_date = DateField('Scheduled Departure Date')
    scheduled_departure_time = TimeField('Scheduled Departure Time')
    submit = SubmitField('Submit')


def current_config_get(final_name, default=None):
    key =f'{CONFIG_PREFIX}{final_name}'
    return current_app.config.get(key, default)

@crewmember_bp.route('/')
def index():
    return redirect(url_for('.query'))

@crewmember_bp.route('/query', methods=['GET', 'POST'])
def query():
    """
    Query database for crew members, jump seats and dead heads.
    """
    result = None
    form = CrewmemberArgsForm(formdata = request.form or request.args)

    if request.method == 'POST':
        if not current_config_get('VALIDATE_FORM', True):
            # allow config to say use the example
            result = EXAMPLE_RESULT
        elif form.validate():
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
            clpconf_path = current_config_get('_CLP_CONFIG')
            # None will cause Exception
            clpconf = central_load_plan.config.process(clpconf_path)
            result = central_load_plan.crewmember.fromdata(clpconf.dbconf, flight_data)

    context = dict(
        form = form,
        interesting_data = INTERESTING_DATA,
        result = result,
    )
    return render_template('crewmember/query.html', **context)

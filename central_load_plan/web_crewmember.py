import datetime

from flask import Blueprint
from flask import Flask
from flask import current_app
from flask import render_template
from flask import request
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
]

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


@crewmember_bp.route('/', methods=['GET', 'POST'])
def query():
    """
    Query database for crew members, jump seats and dead heads.
    """
    result = None
    form = CrewmemberArgsForm(formdata = request.form or request.args)
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
        clpconf_path = current_app.config['CLP_CONFIG']
        clpconf = central_load_plan.config.process(clpconf_path)
        result = central_load_plan.crewmember.fromdata(clpconf.dbconf, flight_data)

    context = dict(
        form = form,
        interesting_data = INTERESTING_DATA,
        result = result,
    )
    return render_template('crewmember/query.html', **context)

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('WEB_CREWMEMBER')
    app.register_blueprint(crewmember_bp)
    return app

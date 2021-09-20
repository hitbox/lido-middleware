import configparser
import glob
import os
import pprint
import textwrap
import xml.etree.ElementTree as ET

from pathlib import Path

import sqlparse

from flask import Blueprint
from flask import Flask
from flask import current_app
from flask import g
from flask import render_template
from flask import request
from wtforms import BooleanField
from wtforms import FileField
from wtforms import Form
from wtforms import SelectField
from wtforms import SubmitField

from . import crewmember
from . import email
from . import pluck
from . import schema
from .utils import keyed_sections
from .schema import oracleconfschema

app_bp = Blueprint('app', __name__)

FILELIST = None

class FormMixin:
    ignorecrew = BooleanField(
        label = 'Ignore Crew',
        render_kw = dict(
            title = 'Avoid hitting database to get crew members',
        ),
    )
    submit = SubmitField('Submit')

class ClientSideXMLForm(Form, FormMixin):

    xmlfile = FileField(
        label = 'OFP XML',
        render_kw = dict(
            title = 'Operational Flight Plan XML file',
        ),
    )


class ServerSideXMLForm(Form, FormMixin):

    # choices added by view
    index = SelectField('Select XML file', coerce=int)


def pathcontext(path, level):
    result = [path]
    for _ in range(level):
        path = path.parent
        result.append(path)
    result.reverse()
    return result

@app_bp.route('/')
def index():
    return render_template('index.html')

@app_bp.route('/from-server', methods=['GET', 'POST'])
def from_server():
    form = ServerSideXMLForm(formdata=request.form)
    form.index.choices = [
        (index, '/'.join(path.name for path in pathcontext(path, 1)))
        for index, path in enumerate(FILELIST)
    ]
    context = {'form': form}
    if request.method == 'POST' and form.validate():
        index = form.index.data
        path = FILELIST[index]
        with open(path) as xmlfile:
            context['result'] = get_output(xmlfile, form.ignorecrew.data)
    return render_template('output.html', **context)

@app_bp.route('/from-client', methods=['GET', 'POST'])
def from_client():
    xmlfile = request.files['xmlfile']
    tree = ET.ElementTree(ET.fromstring(xmlfile.read()))
    root = tree.getroot()
    data = pluck.fromxml(root)
    data = schema.OperationalFlightPlanSchema().load(data)
    ignorecrew = 'ignorecrew' in request.form
    if not ignorecrew:
        # hit database for crew members
        crewresult = crewmember.fromdata(crewmember_config, data)
        data['crewmembers'] = crewresult.crewmembers
    output = email.render_text(data)
    context = dict(
        output = output,
    )
    return render_template('output.html', **context)

def get_output(readable, ignorecrew):
    """
    Return a dict with useful things for displaying what would happen in a real run.
    """
    # XXX: this source -> tree -> pluck -> string_data -> data process is
    #      repeated all over the place because, for example, here, we want to
    #      pass the intermediate steps to the template
    xmlstring = readable.read()
    tree = ET.ElementTree(ET.fromstring(xmlstring))
    root = tree.getroot()
    data = pluck.fromxml(root)
    data = schema.OperationalFlightPlanSchema().load(data)
    if not ignorecrew:
        # hit database for crew members
        crewresult = crewmember.fromdata(current_app.config['CREWMEMBER_CONFIG'], data)
        data['crewmembers'] = crewresult.crewmembers
    airline_iata_code = data['airline_iata_code']
    emailconf = current_app.config['EMAIL_TEMPLATES']
    email_body = email.render(emailconf[airline_iata_code], data)
    result = dict(
        data = data,
        pprint_data = pprint.pformat(data),
        email_body = email_body,
        xmlstring = xmlstring,
    )
    return result

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('CENTRAL_LOAD_PLAN_CONFIG')
    app.register_blueprint(app_bp)

    if 'XMLGLOB' in app.config:
        pathname = app.config['XMLGLOB']
        recursive = '**' in pathname
        global FILELIST
        FILELIST = list(map(Path, glob.glob(pathname, recursive=recursive)))
        if 'XMLGLOB_REVERSE' in app.config and app.config['XMLGLOB_REVERSE']:
            FILELIST.reverse()
        if 'XMLGLOB_LIMIT' in app.config:
            FILELIST = FILELIST[:app.config['XMLGLOB_LIMIT']]

    if 'CREWMEMBER_CONFIG' in app.config:
        cp = configparser.ConfigParser()
        cp.read(app.config['CREWMEMBER_CONFIG'])
        app.config['CREWMEMBER_CONFIG'] = keyed_sections(cp, 'oracle', func=oracleconfschema.load)

    return app


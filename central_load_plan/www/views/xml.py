import configparser
import glob
import os
import pickle
import pprint
import textwrap
import xml.etree.ElementTree as ET

from pathlib import Path

import sqlparse

from flask import Blueprint
from flask import Flask
from flask import current_app
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from wtforms import BooleanField
from wtforms import FileField
from wtforms import Form
from wtforms import SelectField
from wtforms import SubmitField

import central_load_plan.config
import central_load_plan.email
import central_load_plan.pluck
import central_load_plan.schema

from .. import app

CONFIG_PREFIX = f'{app.CONFIG_PREFIX}_XML'

xml_bp = Blueprint('xml', __name__)

# the "database" for this app
database = []

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


def current_config_get(final_name, default=None):
    key =f'{CONFIG_PREFIX}{final_name}'
    return current_app.config.get(key, default)

def pathcontext(path, level):
    result = [path]
    for _ in range(level):
        path = path.parent
        result.append(path)
    result.reverse()
    return result

@xml_bp.route('/')
def index():
    return redirect(url_for('.list'))

@xml_bp.route('/list')
def list():
    context = dict(
        database = database,
    )
    return render_template('from_xml/list.html', **context)

@xml_bp.route('/view/<int:index>')
def view(index):
    xmldata = database[index]
    context = dict(
        xmldata = xmldata,
        message = get_message(xmldata),
    )
    return render_template('from_xml/viewxml.html', **context)

@xml_bp.route('/from-server', methods=['GET', 'POST'])
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

@xml_bp.route('/from-client', methods=['GET', 'POST'])
def from_client():
    xmlfile = request.files['xmlfile']
    tree = ET.ElementTree(ET.fromstring(xmlfile.read()))
    root = tree.getroot()
    data = central_load_plan.pluck.fromxml(root)
    data = schema.OperationalFlightPlanSchema().load(data)
    ignorecrew = 'ignorecrew' in request.form
    if not ignorecrew:
        # hit database for crew members
        crewresult = central_load_plan.crewmember.fromdata(crewmember_config, data)
        data['crewmembers'] = crewresult.crewmembers
    output = central_load_plan.email.render_text(data)
    context = dict(
        output = output,
    )
    return render_template('output.html', **context)

@xml_bp.route('/config')
def config():
    """
    Display how the app is configured.
    """
    config = dict(current_app.config)
    config.update(realappconfig().__dict__)
    return render_template('from_xml/config.html', config=config)

def realappconfig():
    clpconf_path = current_config_get('_CLP_APPCONFIG')
    if not clpconf_path or not os.path.exists(clpconf_path):
        raise ValueError(
            f'Path to real central_load_plan app'
            f'config does not exist, {clpconf_path}')
    clpconf = central_load_plan.config.process(clpconf_path)
    return clpconf

def get_message(data):
    airline_iata_code = data['airline_iata_code']
    clpconf = realappconfig()
    emailconf = clpconf.emailconf[airline_iata_code]
    template = emailconf['template']
    email_body = central_load_plan.email.render(template, data)
    return email_body

@xml_bp.record
def load_glob(state):
    """
    Load data from XML files or cache on register_blueprint.
    """
    with state.app.app_context():
        print('Loading XML')
        xmlcache_path = current_config_get('_CACHE_PATH')
        xml_globs = current_config_get('_GLOBS')
        if not (xmlcache_path or xml_globs):
            raise ValueError('No cache or xml glob configured')

        if xmlcache_path and os.path.exists(xmlcache_path):
            with open(xmlcache_path, 'rb') as pickle_f:
                for xmldata in pickle.load(pickle_f):
                    database.append(xmldata)
        else:
            index = 0
            for xmlglob in xml_globs:
                for source_path in glob.glob(xmlglob):
                    # duplicate app.py:App.process_file
                    if os.stat(source_path).st_size != 0:
                        tree = ET.parse(source_path)
                        root = tree.getroot()
                        strdict = central_load_plan.pluck.fromxml(root)
                        data = central_load_plan.schema.ofpschema.load(strdict)
                        # store original source path for file output
                        data['source_path'] = source_path
                        data['index'] = index
                        database.append(data)
                        index += 1

        if xmlcache_path:
            with open(xmlcache_path, 'wb') as pickle_f:
                pickle.dump(database, pickle_f)

        print('XML Loaded')

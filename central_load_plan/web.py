import configparser
import os
import textwrap
import xml.etree.ElementTree as ET

from flask import Flask
from flask import render_template
from flask import request

from . import crewmember
from . import email
from . import pluck
from . import schema

app = Flask(__name__)

crewmember_config = configparser.ConfigParser()
crewmember_config.read(os.environ['CREWMEMBER_CONFIG'])

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/emailtext', methods=['POST'])
def emailtext():
    xmlfile = request.files['xmlfile']
    tree = ET.ElementTree(ET.fromstring(xmlfile.read()))
    root = tree.getroot()
    data = pluck.fromxml(root)
    data = schema.OperationalFlightPlanSchema().load(data)
    if 'ignorecrew' not in request.form:
        # hit database for crew members
        crewresult = crewmember.fromdata(crewmember_config, data)
        data['crewmembers'] = crewresult.crewmembers
    output = email.render(data)
    context = dict(
        output = output,
        form = request.form,
        crewresult = crewresult,
        textwrap = textwrap,
    )
    return render_template('output.html', **context)

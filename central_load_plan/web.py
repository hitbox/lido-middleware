import configparser
import os
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
    ignorecrew = 'ignorecrew' in request.form
    if not ignorecrew:
        # hit database for crew members
        data['crewmembers'] = crewmember.fromdata(crewmember_config, data)
    output = email.render(data)
    return render_template('emailtext.html', output=output, form=request.form,
                           ignorecrew=ignorecrew)

import configparser
import os
import xml.etree.ElementTree as ET

from flask import Flask
from flask import render_template_string
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
    return render_template_string('''<!doctype html>
<html translate="no">
    <head>
        <title>Central Load Plan Email</title>
        <meta name=google content=notranslate>
        <meta name=viewport content="width=device-width, initial-scale=1.0">
        <link rel="icon" href="data:,">
    </head>
    <body>
        <h1>Central Load Plan Email</h1>
        <p>Select a file click Submit to produce email text.</p>
        <p>All seats will appear as "None"</p>
        <form action="{{ url_for('emailtext') }}" enctype="multipart/form-data" method="post">
            <div>
                <label for="xmlfile">Operational Flight Plan XML file</label>
                <input type="file" id="xmlfile" name="xmlfile">
            </div>
            <input type="submit" value="Submit">
        </form>
    </body>
</html>''')

@app.route('/emailtext', methods=['POST'])
def emailtext():
    xmlfile = request.files['xmlfile']
    tree = ET.ElementTree(ET.fromstring(xmlfile.read()))
    root = tree.getroot()
    data = pluck.fromxml(root)
    data = schema.OperationalFlightPlanSchema().load(data)
    # hit database for crew members
    data['crewmembers'] = crewmember.fromdata(crewmember_config, data)
    output = email.render(data)
    return render_template_string('''
    <div><a href="{{ url_for('main') }}">Process another XML file.</a></div>
    <pre>{{ output }}</pre>''', output=output)

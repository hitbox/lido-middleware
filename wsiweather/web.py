import configparser
import xml.etree.ElementTree as ET

from flask import Flask
from flask import render_template
from flask import request

from . import pluck
from . import schema
from . import wxlmessage

app = Flask(__name__)

@app.route('/')
def main():
    """
    Main form interface to get XML file.
    """
    return render_template('main.html')

@app.route('/output', methods=['POST'])
def output():
    """
    Output result.
    """
    xmlfile = request.files['xmlfile']
    tree = ET.ElementTree(ET.fromstring(xmlfile.read()))
    root = tree.getroot()
    data = pluck.fromxml(root)
    data = schema.WSIWeatherSchema().load(data)
    output = wxlmessage.render(data)
    return render_template('output.html', output=output, form=request.form)

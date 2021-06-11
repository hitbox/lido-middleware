import xml.etree.ElementTree as ET

from pathlib import Path

from flask import Flask
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from . import pluck
from . import schema
from . import wxlmessage

app = Flask(__name__)

app.config.from_envvar('WSIWEATHER_CONFIG')

wsischema = schema.WSIWeatherSchema()

def get_output_path(data):
    output_format = current_app.config['OUTPUT_FORMAT']
    check_until_unique = ''
    while True:
        output_path = output_format.format(
            check_until_unique = check_until_unique,
            **data)
        output_path = Path(output_path)
        if not output_path.exists():
            break
        try:
            check_until_unique = '.' + str(int(check_until_unique.lstrip('.')) + 1)
        except ValueError:
            check_until_unique = '.0'
    return output_path

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
    data = wsischema.load(data)
    message = wxlmessage.render(data)
    output_path = get_output_path(data)
    context = dict(
        data = data,
        data_json = wsischema.dumps(data),
        message = message,
        form = request.form,
        output_path = output_path,
    )
    return render_template('output.html', **context)

@app.route('/write', methods=['POST'])
def write():
    messagetext = request.form['messagetext']
    data_json = request.form['data_json']
    data = wsischema.loads(data_json)
    output_path = get_output_path(data)
    with open(output_path, 'w') as fp:
        fp.write(messagetext)
    flash(f'File written <pre>{output_path}</pre>')
    return redirect(url_for('main'))

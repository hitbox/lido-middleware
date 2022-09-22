import traceback

from pprint import pformat

from flask import Blueprint
from flask import Flask
from flask import current_app
from flask import render_template

from lido import LIDOWeightBalanceMessage

demo_bp = Blueprint('demo', __name__)

class ProcessResult:

    def __init__(self, message, extract_data, schema_data, output):
        self.message = message
        self.extract_data = extract_data
        self.schema_data = schema_data
        self.output = output


def result_or_traceback(func, *args):
    try:
        return func(*args)
    except:
        return traceback.format_exc()

@demo_bp.route('/')
def list():
    data = current_app.config['LIST']
    return render_template('list.html', data=data)

@demo_bp.route('/process/<int:id>')
def process(id):
    data = current_app.config['LIST']
    extract_func = current_app.config['EXTRACT']
    schema_func = current_app.config['SCHEMA']
    output_func = current_app.config['OUTPUT']
    #
    message = data[id]
    extract_data = result_or_traceback(extract_func, message)
    schema_data = result_or_traceback(schema_func, extract_data)
    output = result_or_traceback(output_func, schema_data)
    #
    result = ProcessResult(message, extract_data, schema_data, output)
    return render_template('show_processed.html', result=result)

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('WEBDEMO')
    # raise KeyError for templates and routes
    app.config['EXTRACT']
    app.config['LIST']
    app.config['SCHEMA']
    app.config['TITLE']
    app.config['OUTPUT']
    #
    app.register_blueprint(demo_bp)
    app.add_template_filter(pformat)
    return app

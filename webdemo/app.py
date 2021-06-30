from pprint import pformat

from flask import Blueprint
from flask import Flask
from flask import current_app
from flask import render_template

demo_bp = Blueprint('demo', __name__)

class ProcessResult:

    def __init__(self, message, extract_data):
        self.message = message
        self.extract_data = extract_data


@demo_bp.route('/')
def list():
    data = current_app.config['LIST']
    return render_template('list.html', data=data)

@demo_bp.route('/process/<int:id>')
def process(id):
    data = current_app.config['LIST']
    extract_func = current_app.config['EXTRACT']
    #
    message = data[id]
    extract_data = extract_func(message)
    result = ProcessResult(message, extract_data)
    return render_template('show_processed.html', result=result)

def create_app():
    app = Flask(__name__)
    app.config.from_envvar('APP_CONFIG')
    app.register_blueprint(demo_bp)
    app.add_template_filter(pformat)
    return app

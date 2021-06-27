import pickle
import traceback

from flask import Blueprint
from flask import Flask
from flask import current_app
from flask import render_template

from lido import LIDOWeightBalanceMessage
from sable2 import extract
from sable2 import schema

demo_bp = Blueprint('demo', __name__)

messages = None

@demo_bp.route('/')
def index():
    template = 'list_emails.html'
    return render_template(template, messages=messages)

@demo_bp.route('/<int:index>')
def process(index):
    message = messages[index]

    extract_error = False
    _schema = ''
    _lido = ''
    try:
        _extract = extract.loadplan_from_message(message)
    except:
        extract_error = True
        _extract = traceback.format_exc()
    else:
        try:
            _schema = schema.LoadPlanSchema().load(_extract)
        except:
            _schema = traceback.format_exc()
        else:
            try:
                _lido = LIDOWeightBalanceMessage(_schema, bypass_length_check=True)
            except:
                _lido = traceback.format_exc()
    context = dict(
        message = message,
        extract = _extract,
        extract_error = extract_error,
        schema = _schema,
        lido = _lido,
    )
    return render_template('show_processed.html', **context)

def create_app():
    app = Flask(__name__)

    app.config.from_envvar('SABLEV2')
    app.register_blueprint(demo_bp)

    app.add_template_filter(repr)

    with open(app.config['MESSAGES_PICKLE'], 'rb') as fp:
        global messages
        messages = pickle.load(fp)

    return app

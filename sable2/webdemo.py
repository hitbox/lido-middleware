import pickle
import traceback

from pprint import pformat

from flask import Blueprint
from flask import Flask
from flask import current_app
from flask import render_template

from lido import LIDOWeightBalanceMessage

from . import extract
from . import schema

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
    schema_error = False
    lido_error = False
    render_lido_error = False

    _schema = ''
    _lido = ''
    rendered_lido_message = ''
    try:
        _extract = extract.loadplan_from_message(message)
    except:
        extract_error = True
        _extract = traceback.format_exc()
    else:
        try:
            _schema = schema.LoadPlanSchema().load(_extract)
        except:
            schema_error = True
            _schema = traceback.format_exc()
        else:
            try:
                _lido = LIDOWeightBalanceMessage(_schema, bypass_length_check=True)
            except:
                lido_error = True
                _lido = traceback.format_exc()
            else:
                try:
                    rendered_lido_message = str(_lido)
                except:
                    render_lido_error = True
                    rendered_lido_message = traceback.format_exc()
    context = dict(
        message = message,
        extract = _extract,
        extract_error = extract_error,
        schema = _schema,
        schema_error = schema_error,
        lido = _lido,
        lido_error = lido_error,
        rendered_lido_message = rendered_lido_message,
        render_lido_error = render_lido_error,
    )
    return render_template('show_processed.html', **context)

def create_app():
    app = Flask(__name__)

    app.config.from_envvar('SABLEV2')
    app.register_blueprint(demo_bp)

    app.add_template_filter(repr)
    app.add_template_filter(pformat)

    with open(app.config['MESSAGES_PICKLE'], 'rb') as fp:
        global messages
        messages = pickle.load(fp)

    return app

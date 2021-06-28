import pickle
import traceback

from pprint import pformat

from flask import Blueprint
from flask import Flask
from flask import render_template

from lido import LIDOWeightBalanceMessage

from . import extract
from . import schema

demo_bp = Blueprint('demo', __name__)

messages = None

class Step:

    def __init__(self, name, func, *args, post=None):
        self.name = name
        self.func = func
        self.args = args
        self.return_value = None
        self.is_error = None
        self.traceback_message = None
        self.post = post

    def try_step(self, *args):
        args = self.args + args
        try:
            self.return_value = self.func(*args)
        except:
            self.traceback_message = traceback.format_exc()
            self.is_error = True
        else:
            return self.return_value

    @property
    def html_text(self):
        func = self.post if callable(self.post) else lambda v: v
        return func(self.return_value)


def mklidomessage(data):
    msg = LIDOWeightBalanceMessage(data)
    return str(msg)

def process_steps(message):
    steps = [
        Step('Extract', extract.loadplan_from_message, message, post=pformat),
        Step('Schema', schema.LoadPlanSchema().load, post=pformat),
        Step('LIDO Message', mklidomessage),
    ]
    args = tuple()
    for step in steps:
        rv = step.try_step(*args)
        if step.is_error:
            break
        args = (rv,)
    return steps

@demo_bp.route('/')
def index():
    return render_template('list_emails.html', messages=messages)

@demo_bp.route('/<int:index>')
def process(index):
    message = messages[index]
    steps = process_steps(message)
    context = dict(
        message = message,
        steps = steps,
    )
    return render_template('show_processed.html', **context)

def create_app():
    app = Flask(__name__)

    app.config.from_envvar('PISTOL2')
    app.register_blueprint(demo_bp)

    app.add_template_filter(pformat)
    app.add_template_filter(repr)

    with open(app.config['MESSAGES_PICKLE'], 'rb') as fp:
        global messages
        messages = pickle.load(fp)[20:][::-1]

    return app

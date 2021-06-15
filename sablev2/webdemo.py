import pickle

from flask import Blueprint
from flask import Flask
from flask import current_app
from flask import render_template

from lido import LIDOWeightBalanceMessage
from sablev2.extract import loadplan_from_message
from sablev2.schema import LoadPlanSchema

demo_bp = Blueprint('demo', __name__)

messages = None

class Demo:

    def __init__(self):
        self.original_text = None
        self.extracted = None
        self.schemafied = None
        self.lidomessage = None

    def build_from_email(self, email):
        self.extracted = loadplan_from_message(email)
        schema = LoadPlanSchema()
        self.schemafied = schema.load(self.extracted)
        self.lidomessage = LIDOWeightBalanceMessage(self.schemafied)


@demo_bp.route('/')
def index():
    template = 'list_emails.html'
    return render_template(template, messages=messages)

@demo_bp.route('/<int:index>')
def process(index):
    email = messages[index]
    demo = Demo()
    demo.build_from_email(email)
    template = 'show_processed.html'
    return render_template(template, demo=demo)

def create_app():
    app = Flask(__name__)

    app.config.from_envvar('SABLEV2')
    app.register_blueprint(demo_bp)

    with open(app.config['MESSAGES_PICKLE'], 'rb') as fp:
        global messages
        messages = pickle.load(fp)

    return app

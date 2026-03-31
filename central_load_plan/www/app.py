from flask import Flask
from flask import render_template

from . import converter
from . import extension
from . import views

CONFIG_PREFIX = 'CENTRAL_LOAD_PLAN'

def create_app():
    """
    Demo web apps for central_load_plan.
    """
    app = Flask(__name__)
    app.config.from_envvar(f'{CONFIG_PREFIX}_CONFIG')

    extension.init_app(app)
    converter.init_app(app)
    views.init_app(app)

    @app.route('/')
    def index():
        """
        List of links to enabled views' indexes.
        """
        return render_template('index.html', blueprints=app.blueprints)

    @app.cli.command('create-db')
    def create_db():
        from central_load_plan.www.extension import db
        db.create_all()

    return app

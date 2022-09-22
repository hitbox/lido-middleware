from flask import Flask
from flask import redirect
from flask import url_for

from .views.run import run_bp

def create_app():
    """
    Web app to demonstrate what happens in run/run.py
    """
    app = Flask(__name__)
    app.config.from_envvar('RUN')

    @app.route('/')
    def index():
        return redirect(url_for('run.list_run_configs'))

    @app.context_processor
    def inject_context():
        return {
            'repr': repr,
        }

    app.register_blueprint(run_bp)
    return app

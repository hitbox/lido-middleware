from flask import Flask
from flask import render_template

CONFIG_PREFIX = 'CENTRAL_LOAD_PLAN'

def create_app():
    """
    Demo web apps for central_load_plan.
    """
    app = Flask(__name__)
    app.config.from_envvar(f'{CONFIG_PREFIX}')

    # matching config names with a truthy value to optionally hook up blueprints

    if app.config.get(f'{CONFIG_PREFIX}_CREWMEMBERS'):
        from .views.crewmembers import crewmember_bp
        app.register_blueprint(crewmember_bp, url_prefix='/crewmembers')

    if app.config.get(f'{CONFIG_PREFIX}_XML'):
        from .views.xml import xml_bp
        app.register_blueprint(xml_bp, url_prefix='/xml')

    @app.route('/')
    def index():
        """
        List of links to enabled views' indexes.
        """
        return render_template('index.html', blueprints=app.blueprints)

    return app

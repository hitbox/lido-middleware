import datetime

from flask import Blueprint
from flask import render_template
from flask import current_app

import lido
import run.config
import run.run

run_bp = Blueprint('run', __name__, url_prefix='/runs')

def get_run_configs():
    """
    Convenience function to get a named mapping of run configs.
    """
    run_configs = current_app.config['RUN_CONFIGS']
    return run_configs

def get_named_run_config(name):
    run_configs = get_run_configs()
    run_config = run_configs[name]
    return run_config

def get_real_config(run_config):
    """
    Load the configuration for a run from Python file.
    """
    real_config_path = run_config['config']
    real_config = run.config.pyfile_config(real_config_path)
    return real_config

@run_bp.route('/')
def list_run_configs():
    """
    Run configurations listing.
    """
    run_configs = get_run_configs()
    context = dict(
        run_configs = run_configs,
    )
    return render_template('list_run_configs.html', **context)

@run_bp.route('/<name>')
def view_run_config(name):
    """
    Preview run configuration
    """
    run_config = get_named_run_config(name)
    context = dict(
        run_config = run_config,
        PYFILE_CONFIG = get_real_config(run_config),
    )
    return render_template('view_run_config.html', **context)

@run_bp.route('/run/<name>')
def run_named_config(name):
    """
    Run a Lido middleware configuration.
    """
    run_start = datetime.datetime.now()
    run_config = get_named_run_config(name)
    real_config = get_real_config(run_config)

    # TODO: better namespace
    run_instance = run.run.run
    # NOTE: using the method that gathers results
    run_result = run_instance.run(
        source = real_config['SOURCE'],
        schema_class = real_config['SCHEMA_CLASS'],
        message_filter = run.config.PassMessageFilter(),
        message_processor = real_config['MESSAGE_PROCESSOR'],
        output = run.config.NullOutput(
            real_config['OUTPUT'].pathfmt,
        ),
        message_archive = run.config.PassSHA1GraphMessageArchive(None),
        message_class = real_config.get('MESSAGE_CLASS', lido.LIDOWeightBalanceMessage),
        raise_exc = False,
        # TODO: airline_mapping
    )

    context = dict(
        run_result = run_result,
        run_start = run_start,
    )
    return render_template('run_result.html', **context)

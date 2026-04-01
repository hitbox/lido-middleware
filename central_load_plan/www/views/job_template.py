import csv
import datetime
import glob
import os
import re

import click
import sqlalchemy as sa

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy.orm import Session

import central_load_plan.crewmember

from central_load_plan.constants import AIRLINE_CODES
from central_load_plan.engine import get_lsyrept_engine
from central_load_plan.flight_plan_parser import FlightPlanParser
from central_load_plan.models import ChainItemDaily
from central_load_plan.models import JobTemplate
from central_load_plan.models import Duty
from central_load_plan.models import ItemDaily
from central_load_plan.models import LSYBase
from central_load_plan.models import NonCrewMember
from central_load_plan.models import OFPCondition
from central_load_plan.models import OFPFile
from central_load_plan.models import RemarkOfEvent
from central_load_plan.models.lsyrept import crew_members_from_ofp
from central_load_plan.schema import EFFArchivePathSchema
from central_load_plan.schema import OperationalFlightPlanSchema
from central_load_plan.schema import lsyrept_model_schemas
from central_load_plan.www.extension import db
from central_load_plan.www.extension import login_manager
from central_load_plan.www.form import CrewmemberArgsForm
from central_load_plan.www.form import EFFArchiveFilterForm

job_template_bp = Blueprint('job_template', __name__)

@job_template_bp.before_request
def require_login():
    if not current_user.is_authenticated:
        return login_manager.unauthorized()


@job_template_bp.route('/')
def index():
    return redirect(url_for('.query'))


@job_template_bp.route('/from-ofp-file/<uuid:id>')
def from_ofp_file(id):
    """
    Matching job templates from ofp file.
    """
    ofp_file = db.session.get(OFPFile, id)
    if ofp_file is None:
        abort(404)

    matches = []
    for job_template in db.session.scalars(db.select(JobTemplate)):
        if job_template.ofp_condition.is_match(ofp_file):
            href = url_for(
                "job_template.preview_job_template_for_file",
                job_template_id = job_template.id,
                ofp_file_id = ofp_file.id,
            )
            matches.append(Markup(f'<a href="{href}">{job_template.name}</a>'))

    context = {
        'title': Markup(f'Matching jobs for file <pre>{ ofp_file.archive_path }</pre>'),
        'list_items': matches,
    }
    return render_template('unordered_list.html', **context)

@job_template_bp.route('/preview/<uuid:job_template_id>/<uuid:ofp_file_id>')
def preview_job_template_for_file(job_template_id, ofp_file_id):
    job_template = db.session.get(JobTemplate, job_template_id)

    if job_template is None:
        abort(404)

    ofp_file = db.session.get(OFPFile, ofp_file_id)
    if ofp_file is None:
        abort(404)

    context = {
        'markup': job_template.html_preview(ofp_file),
    }
    return render_template('basic.html', **context)

@job_template_bp.cli.command('list-for-crew')
def list_for_crew():
    """
    Trying to find an OFPFile with crew coming back from the LSY queries
    """

    for ofp_file in db.session.scalars(db.select(OFPFile)):
        click.echo(ofp_file.archive_path)
        ofp_data = ofp_file.as_dict_with_crew()
        if ofp_data['crew_members']:
            breakpoint()

import sqlalchemy as sa

from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.views import View

from central_load_plan.www.extension import db

class ListView(View):
    """
    Queryable database object view.
    """

    def __init__(self, model, template, table, edit_endpoint, create_endpoint):
        self.model = model
        self.template = template
        self.table = table
        self.edit_endpoint = edit_endpoint
        self.create_endpoint = create_endpoint

    def dispatch_request(self, **kwargs):
        pagination = db.paginate(db.select(self.model))
        context = {
            'model': self.model,
            'table': self.table,
            'pagination': pagination,
            'edit_endpoint': self.edit_endpoint,
            'create_endpoint': self.create_endpoint,
        }
        return render_template(self.template, **context)

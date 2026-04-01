"""
Named instances of database objects that must exist for application to work.
"""

from central_load_plan.models import OFPCondition
from central_load_plan.www.extension import db

class CoreObjects:

    @property
    def abx_ofp_condition(self):
        query = db.select(OFPCondition).where(OFPCondition.name == 'ABX OFP')
        return db.session.scalars(query).one()

    @property
    def ati_ofp_condition(self):
        query = db.select(OFPCondition).where(OFPCondition.name == 'ATI OFP')
        return db.session.scalars(query).one()

    @property
    def abx_and_ati_ofp_condition(self):
        query = db.select(OFPCondition).where(OFPCondition.name == 'ABX or ATI')
        return db.session.scalars(query).one()

instances = CoreObjects()

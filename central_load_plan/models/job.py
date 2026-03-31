import uuid

from enum import Enum

import sqlalchemy as sa

from .clp_base import CLPBase

class JobTypeEnum(Enum):
    """
    Some type of work to do with OFP data scraped from XML files.
    """

    SEND_EMAIL = 'send_email'

    WRITE_FILE = 'write_file'

    def instance(self):
        from central_load_plan.www.extension import db

        query = db.select(JobType).where(JobType.name == self.name)
        return db.session.scalars(query).one()


class JobType(CLPBase):
    """
    Type of Job to conditionally perform on OFP files.
    """

    __tablename__ = 'job_type'

    id = sa.Column(sa.Uuid, primary_key=True, default=uuid.uuid4)

    name = sa.Column(sa.String, nullable=False, unique=True)


class JobTemplate(CLPBase):
    """
    Named template for work to do when a condition is met against an OFPFile object.
    """

    __tablename__ = 'job_template'

    id = sa.Column(sa.Uuid, primary_key=True, default=uuid.uuid4)

    name = sa.Column(sa.String, nullable=False, unique=True)

    ofp_condition_id = sa.Column(sa.ForeignKey('ofp_condition.id'))

    ofp_condition = sa.orm.relationship(
        'OFPCondition',
    )

    job_type_id = sa.Column(sa.ForeignKey('job_type.id'))

    parameters = sa.Column(sa.JSON, nullable=False)

    def make_job(self, ofp_file):
        return Job(
            job_type = self.job_type,
            ofp_file = self.ofp_file,
            parameters = self.parameters,
        )



class Job(CLPBase):
    """
    Some work to do with OFP data.
    """

    __tablename__ = 'job'

    id = sa.Column(sa.Uuid, primary_key=True, default=uuid.uuid4)

    job_type_id = sa.Column(sa.ForeignKey('job_type.id'))

    ofp_file_id = sa.Column(sa.ForeignKey('ofp_file.id'))

    ofp_file = sa.orm.relationship(
        'OFPFile',
        back_populates = 'jobs',
    )

    parameters = sa.Column(sa.JSON, nullable=False)

import uuid

import sqlalchemy as sa

from .clp_base import CLPBase

class Email(CLPBase):

    __tablename__ = 'email'

    id = sa.Column(sa.Uuid, primary_key=True, default=uuid.uuid4)

    address = sa.Column(sa.String, unique=True, nullable=False)

    display_name = sa.Column(sa.String, nullable=True)

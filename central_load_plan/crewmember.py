import argparse
import json
import logging
import sys

from datetime import date
from datetime import datetime
from datetime import time
from types import SimpleNamespace

import sqlalchemy as sa

from sqlalchemy.exc import OperationalError

from central_load_plan.models.lsyrept import ChainItemDaily
from central_load_plan.models.lsyrept import LSYCrewMember
from central_load_plan.models.lsyrept import Duty
from central_load_plan.models.lsyrept import ItemDaily
from central_load_plan.models.lsyrept import NonCrewMember
from central_load_plan.models.lsyrept import RemarkOfEvent

class CrewMemberResult:
    """
    Simple structure holding crewmembers and metadata so that the web app can
    display useful info.
    """

    def __init__(self, crewmembers, query, data, engine):
        self.crewmembers = crewmembers
        self.query = query
        self.data = data
        self.engine = engine

    def __bool__(self):
        return bool(self.crewmembers)

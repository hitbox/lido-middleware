from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy import auto_field

from central_load_plan.models.lsyrept import ChainItemDaily
from central_load_plan.models.lsyrept import CrewMember
from central_load_plan.models.lsyrept import Duty
from central_load_plan.models.lsyrept import ItemDaily
from central_load_plan.models.lsyrept import NonCrewMember
from central_load_plan.models.lsyrept import RemarkOfEvent

class ChainItemDailySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ChainItemDaily


class CrewMemberSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CrewMember


class DutySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Duty


class ItemDailySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ItemDaily


class NonCrewMemberSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = NonCrewMember


class RemarkOfEventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = RemarkOfEvent


# lookup schema from model
lsyrept_model_schemas = {
    ChainItemDaily: ChainItemDailySchema,
    CrewMember: CrewMemberSchema,
    Duty: DutySchema,
    ItemDaily: ItemDailySchema,
    NonCrewMember: NonCrewMemberSchema,
    RemarkOfEvent: RemarkOfEventSchema,
}

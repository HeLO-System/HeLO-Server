from marshmallow import Schema, ValidationError, fields
from marshmallow.validate import Range


class SimulationsSchema(Schema):
    clans1_ids = fields.List(fields.String, required=True)
    clans2_ids = fields.List(fields.String, required=True)
    caps1 = fields.Integer(required=True, validate=Range(min=0, max=5, min_inclusive=True, max_inclusive=True))
    caps2 = fields.Integer(required=True, validate=Range(min=0, max=5, min_inclusive=True, max_inclusive=True))
    player_dist1 = fields.List(fields.Integer(validate=Range(min=0, max=50, min_inclusive=True, max_inclusive=True)))
    player_dist2 = fields.List(fields.Integer(validate=Range(min=0, max=50, min_inclusive=True, max_inclusive=True)))

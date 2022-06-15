from marshmallow import Schema, fields
from marshmallow.validate import Range, OneOf


class SimulationsSchema(Schema):
    clans1_ids = fields.List(fields.String, required=True)
    clans2_ids = fields.List(fields.String, required=True)
    caps1 = fields.Integer(required=True, validate=Range(min=0, max=5, min_inclusive=True, max_inclusive=True))
    caps2 = fields.Integer(required=True, validate=Range(min=0, max=5, min_inclusive=True, max_inclusive=True))
    player_dist1 = fields.List(fields.Integer(validate=Range(min=0, max=50, min_inclusive=True, max_inclusive=True)))
    player_dist2 = fields.List(fields.Integer(validate=Range(min=0, max=50, min_inclusive=True, max_inclusive=True)))
    players = fields.Integer(validate=Range(min=3, max=50, max_inclusive=True))
    factor = fields.Float(validate=OneOf([0.3, 0.6, 2.0, 2.4]))

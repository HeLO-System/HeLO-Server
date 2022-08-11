from marshmallow import Schema, ValidationError, fields
from marshmallow.validate import OneOf, Length, And, Range, Regexp, Validator, Predicate
import typing

from models.clan import Clan
from models.match import Match
from models.score import Score

# example to chain multiple validators:
# tag = fields.String(validate=And(Length(max=10), OneOf(["name"])))

class In(Validator):
# custom validator class,
# checks if all passed values are in a passed iterable

    def __init__(self, attrs: typing.Iterable):
        self.attrs = attrs
        
    def _format_error(self, faulty_value) -> str:
        return f'{faulty_value} is not a valid parameter for selection'

    def __call__(self, value: typing.Any) -> typing.Any:
        try:
            # all attributes to possibly select from
            attrs = set(self.attrs)
            # check if the selected values are all in attrs
            values_in = [val in attrs for val in value.split(",")]
            if not all(values_in):
                faulty_value = value.split(",")[values_in.index(False)]
                raise ValidationError(self._format_error(faulty_value))
        except TypeError as e:
            raise ValidationError(self._format_error(faulty_value)) from e
        return value
    

def validate_side(x: str):
    if x.casefold() in ("axis", "allies"):
        return True
    raise ValidationError("Invalid value. Must be one of ('axis', 'allies')")
        

# Schema for queries on '/clans'
class ClanQuerySchema(Schema):
    tag = fields.String(validate=Length(max=10))
    name = fields.String()
    num_matches = fields.Integer(validate=Range(min=0, min_inclusive=True))
    score_from = fields.Integer(validate=Range(min=0, min_inclusive=True))
    score_to = fields.Integer(validate=Range(min=0, min_inclusive=True))
    limit = fields.Integer(validate=Range(min=0, min_inclusive=True))
    offset = fields.Integer(validate=Range(min=0, min_inclusive=True))
    sort_by = fields.String(validate=OneOf(["tag", "name", "score", "num_matches"]))
    select = fields.String(validate=In(Clan.__dict__.keys()))
    # TODO: make this better
    desc = fields.Boolean()
    archived = fields.Boolean()


# Schema for queries in '/matches'
class MatchQuerySchema(Schema):
    select = fields.String(validate=In(Match.__dict__.keys()))
    match_id = fields.String()
    clan_ids = fields.String()
    caps = fields.Integer(validate=Range(min=0, max=5, min_inclusive=True, max_inclusive=True))
    caps_from = fields.Integer(validate=Range(min=0, max=5, min_inclusive=True, max_inclusive=True))
    map = fields.String()
    duration_from = fields.Integer(validate=Range(min=8, max=90, min_inclusive=True, max_inclusive=True))
    duration_to = fields.Integer(validate=Range(min=8, max=90, min_inclusive=True, max_inclusive=True))
    factor = fields.Float(validate=OneOf([0.3, 0.6, 2.0, 2.4]))
    conf = fields.String()
    event = fields.String()
    limit = fields.Integer(validate=Range(min=0, min_inclusive=True))
    offset = fields.Integer(validate=Range(min=0, min_inclusive=True))
    sort_by = fields.String(validate=OneOf(["match_id", "date", "players", "caps1", "factor", "score_posted", "clans1_ids", "clans2_ids"]))
    date = fields.Date()
    date_from = fields.Date()
    date_to = fields.Date()
    desc = fields.Boolean()


# Schema for queries on '/search'
class SearchQuerySchema(Schema):
    # query string
    q = fields.String(required=True)
    # type
    type = fields.String(required=True, validate=OneOf(["clan", "match", "score"]))
    limit = fields.Integer(validate=Range(min=0, min_inclusive=True))
    offset = fields.Integer(validate=Range(min=0, min_inclusive=True))
    sort_by = fields.String(validate=OneOf(["clan", "match_id", "score", "num_matches", "_created_at"]))
    desc = fields.Boolean()


# Schema for queries in '/scores'
class ScoreQuerySchema(Schema):
    select = fields.String(validate=In(Score.__dict__.keys()))
    clan_id = fields.String()
    match_id = fields.String()
    num_matches = fields.Integer(validate=Range(min=0, min_inclusive=True))
    num_matches_from = fields.Integer(validate=Range(min=0, min_inclusive=True))
    num_matches_to = fields.Integer(validate=Range(min=0, min_inclusive=True))
    score = fields.Integer(validate=Range(min=0, min_inclusive=True))
    score_from = fields.Integer(validate=Range(min=0, min_inclusive=True))
    score_to = fields.Integer(validate=Range(min=0, min_inclusive=True))
    limit = fields.Integer(validate=Range(min=0, min_inclusive=True))
    offset = fields.Integer(validate=Range(min=0, min_inclusive=True))
    sort_by = fields.String(validate=OneOf(["tag", "name", "score", "num_matches"]))
    desc = fields.Boolean()


# Schema for queries in '/clan/<oid>/score_history'
class ScoreHistoryQuerySchema(Schema):
    start = fields.Date()
    end = fields.Date()
    select = fields.String(validate=In(Score.__dict__.keys()))
    desc = fields.Boolean()


# Schema for queries in '/statistics/winrate/{oid}'
class StatisticsQuerySchema(Schema):
    map = fields.String()
    side = fields.String(validate=validate_side)
    as_img = fields.Boolean() # only for console

class SimulationsQuerySchema(Schema):
    ignore = fields.String(validate=In(["factor", "num_matches", "players"]))

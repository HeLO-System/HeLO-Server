from marshmallow import Schema, ValidationError, fields
from marshmallow.validate import OneOf, Length, And, Range, Validator
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
    
        

# Schema for queries on '/clans'
class ClanQuerySchema(Schema):
    tag = fields.String(validate=Length(max=10))
    name = fields.String()
    num_matches = fields.Integer(validate=Range(min_inclusive=0))
    score_from = fields.Integer(validate=Range(min_inclusive=0))
    score_to = fields.Integer(validate=Range(min_inclusive=0))
    limit = fields.Integer(validate=Range(min_inclusive=0))
    offset = fields.Integer(validate=Range(min_inclusive=0))
    sort_by = fields.String(validate=OneOf(["tag", "name", "score", "num_matches"]))
    select = fields.String(validate=In(Clan.__dict__.keys()))
    # TODO: make this better
    desc = fields.Boolean()


# Schema for queries in '/matches'
class MatchQuerySchema(Schema):
    select = fields.String(validate=In(Match.__dict__.keys()))
    match_id = fields.String()
    clan_ids = fields.String()
    caps = fields.Integer(validate=Range(min_inclusive=0, max_inclusive=5))
    caps_from = fields.Integer(validate=Range(min_inclusive=0, max_inclusive=5))
    map = fields.String()
    duration_from = fields.Integer(validate=Range(min_inclusive=8, max_inclusive=90))
    duration_to = fields.Integer(validate=Range(min_inclusive=8, max_inclusive=90))
    factor = fields.Float(validate=OneOf([0.5, 0.8, 1.0, 1.2]))
    conf = fields.String()
    event = fields.String()
    limit = fields.Integer(validate=Range(min_inclusive=0))
    offset = fields.Integer(validate=Range(min_inclusive=0))
    sort_by = fields.String(validate=OneOf(["tag", "name", "score", "num_matches"]))
    date = fields.String()
    date_from = fields.String()
    date_to = fields.String()
    desc = fields.Boolean()


# Schema for queries on '/search'
class SearchQuerySchema(Schema):
    # query string
    q = fields.String(required=True)
    # type
    type = fields.String(required=True, validate=OneOf(["clan", "match", "score"]))
    limit = fields.Integer(validate=Range(min_inclusive=0))
    offset = fields.Integer(validate=Range(min_inclusive=0))
    sort_by = fields.String(validate=OneOf(["tag", "name", "score", "num_matches"]))
    desc = fields.Boolean()


# Schema for queries in '/scores'
class ScoreQuerySchema(Schema):
    select = fields.String(validate=In(Score.__dict__.keys()))
    clan_id = fields.String()
    match_id = fields.String()
    num_matches = fields.Integer(validate=Range(min_inclusive=0))
    num_matches_from = fields.Integer(validate=Range(min_inclusive=0))
    num_matches_to = fields.Integer(validate=Range(min_inclusive=0))
    score = fields.Integer(validate=Range(min_inclusive=0))
    score_from = fields.Integer(validate=Range(min_inclusive=0))
    score_to = fields.Integer(validate=Range(min_inclusive=0))
    limit = fields.Integer(validate=Range(min_inclusive=0))
    offset = fields.Integer(validate=Range(min_inclusive=0))
    sort_by = fields.String(validate=OneOf(["tag", "name", "score", "num_matches"]))
    desc = fields.Boolean()


# Schema for queries in '/clan/<oid>/score_history'
class ScoreHistoryQuerySchema(Schema):
    start = fields.Date()
    end = fields.Date()
    select = fields.String(validate=In(Score.__dict__.keys()))
    desc = fields.Boolean()

"""
class to store all scores from all clans, this class should be understood as QoL class,
that make things easier in the long run, but should not be considered as "first level class"
Every new score will be stored in a Score object. The maximum amount of score objects
for one clan is the sum of all matches of the clan.
One match results automatically in at least two Score Objects.
"""

import json
from datetime import datetime

from database.db import db, CustomQuerySet


class Score(db.Document):
    clan = db.StringField(required=True)
    # number of games, = 31 means it's the score gained from the 31st match
    num_matches = db.IntField(required=True)
    # match id of the match where the score calculation
    # is based on, something like "StDb-91.-2022-01-07"
    match_id = db.StringField(required=True)
    score = db.IntField(required=True)
    # private property, should be readed only
    # TODO: implement real protection
    _created_at = db.DateTimeField(default=datetime.now())
    # redundant, because with "count" and "clan" we can extract the old score
    # besides when creating the Score object, we don't need to care about
    # double checking whether the score in the corresponding clan object is the same
    # IMPORTANT: clan.score must be updated first!
    # score_before = db.IntField(required=True)
    meta = {
            "indexes": [
                {
                    "fields": ["$match_id"]
                }
            ],
            "queryset_class": CustomQuerySet
        }

    def __init__(self, clan: str, num_matches: int, match_id: str, score: int, *args, **kwargs):
        super().__init__()
        self.clan = clan
        self.num_matches = num_matches
        self.match_id = match_id
        self.score = score

    @classmethod
    def from_match(cls, match, clan):
        """Alternative constructor.

        Args:
            match (Match): Match object the calculation is based on
            clan (Clan): Clan that the score belongs to

        Returns:
            Score: the new Score object
        """
        # clan.id is the oid of the Clan object in the DB
        return cls(str(clan.id), clan.num_matches, match.match_id, clan.score)


    def to_dict(self):
        return json.loads(self.to_json())

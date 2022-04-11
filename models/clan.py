"""
first level class
"""

from database.db import db


class Clan(db.Document):
    # e.g. StDb for Stoßtrupp Donnerbalken
    tag = db.StringField(required=True, unique=True)
    # full name
    name = db.StringField()
    # discord icon flag, e.g. :flag_eu:, :flag_de:, ...
    flag = db.StringField()
    # discord invite link to a clan's discord server
    invite = db.StringField()
    # current HeLO Score
    score = db.IntField(default=600)
    # number of games
    num_matches = db.IntField(default=0)
    # confirmation, reserved ??
    conf = db.StringField()
    # alternative tags, if a clan was renamed, reserved
    alt_tags = db.ListField()
    # link to the icon of a clan
    icon = db.StringField(default="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fcdn.onlinewebfonts.com%2Fsvg%2Fimg_189144.png&f=1&nofb=1")
    meta = {
        "indexes": [
            {
                "fields": ["$tag", "$name"]
            }
        ]
    }


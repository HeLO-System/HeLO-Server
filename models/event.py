"""
first level class
"""

from database.db import db


class Event(db.Document):
    # acronym of the event, like HPL = Hell Let Loose Premier League
    tag = db.StringField(required=True, unique=True)
    # corresponding name to the tag
    name = db.StringField()
    # event emoji, e.g. :hpl:
    emoji = db.StringField()
    # factor for score, e.g. extra sweaty = 1.2
    factor = db.FloatField()
    # discord invite link to the event's discord server
    invite = db.StringField()
    # confirmation, reserved ??
    conf = db.StringField()

"""
second level class
"""
import json
from enum import Enum

from database.db import CustomQuerySet, db
from flask_bcrypt import check_password_hash, generate_password_hash


class Role(Enum):
    User = 'USER'
    Admin = 'ADMIN'
    TeamManager = 'TEAM_MANAGER'

class User(db.Document):
    # discord id, very long number
    userid = db.StringField(required=True, unique=True)
    # required for login
    pin = db.StringField()
    name = db.StringField()
    # admin or teamrep (team representative)
    role = db.StringField(required=True)
    clan = db.StringField()
    # confirmation of a user (id), reserved ??
    conf = db.StringField()
    meta = {
        "queryset_class": CustomQuerySet
    }
 
    def hash_password(self):
        self.pin = generate_password_hash(self.pin).decode('utf8')
 
    def check_password(self, pin):
        return check_password_hash(self.pin, pin)

    def to_dict(self):
        return json.loads(self.to_json())

from database.db import db, CustomQuerySet


class ConsoleImage(db.Document):
    image = db.FileField(db_alias="console") # for the GridFS stuff like chunks
    meta = {"db_alias": "console"} # for the ConsoleImage object itself

import datetime
from ..db import db
import mongoengine_goodjson as gj


class TokenBlockList(gj.Document):
    jti = db.StringField(required=True)
    created_at = db.DateTimeField(default=datetime.datetime.now())

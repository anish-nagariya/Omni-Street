import datetime
from ..db import db
import mongoengine_goodjson as gj


class Account(gj.Document):
    username = db.StringField(required=True, unique=True)
    password = db.StringField(required=True, unique=True, min_length=6)
    firstName = db.StringField()
    lastName = db.StringField()
    email = db.EmailField(required=True, unique=True)
    role = db.StringField(default='User')
    resetToken = db.StringField(null=True)
    verificationToken = db.StringField(null=True)
    dateCreated = db.DateTimeField(default=datetime.datetime.now())
    isVerified = db.BooleanField(default=False)
    symbols = db.ListField(db.StringField())

    def generateDict(self):
        return {'username': self.username, 'firstName': self.firstName, 'lastName': self.lastName, 'email': self.email, 'role': self.role}

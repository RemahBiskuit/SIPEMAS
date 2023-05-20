from app import db
from flask_login import UserMixin
from datetime import datetime

class Users(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True)
    email         = db.Column(db.String(64), unique=True)
    password      = db.Column(db.String(150))
    oauth_github  = db.Column(db.String(100), nullable=True)
    nama          = db.Column(db.String(255))
    alamat        = db.Column(db.String(255))
    notelp        = db.Column(db.String(255))
    gender        = db.Column(db.String(255))
    id_role       = db.Column(db.Integer, default=2)

    def __repr__(self):
        return f'{self.username} : {self.email}'
    
class Roles(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    role          = db.Column(db.String(64))
# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100),unique = True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(200))
    links = db.relationship('Link', backref='owner')



class Link(db.Model):
    """ Create link table"""
    id = db.Column(db.Integer, primary_key=True)
    key_word = db.Column(db.String(80))
    link = db.Column(db.String(400))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #user = db.relationship("User")


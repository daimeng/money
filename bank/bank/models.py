import hashlib
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from bank.db import db


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String, unique=True, nullable=False)
    pin_encrypted = db.Column(db.String, nullable=False)
    # PIN is short, salt to help impede rainbow tables
    salt = db.Column(db.String, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=False), default=datetime.utcnow, nullable=False
    )


class Session(db.Model):
    token = db.Column(db.String, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=False), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=False), default=datetime.utcnow, nullable=False
    )


class Exchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    amount = db.Column(
        db.Numeric(precision=13, scale=4, asdecimal=True), nullable=False
    )
    party = db.Column(db.String, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=False), default=datetime.utcnow, nullable=False
    )

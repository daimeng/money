import os
import binascii
from decimal import Decimal

from hashlib import pbkdf2_hmac
from flask import g

from bank.models import Exchange
from bank.db import db


def get_balance(account_id):
    """Helper to get current account balance"""
    return (
        db.session.query(db.func.SUM(Exchange.amount))
        .filter(Exchange.account_id == g.session.account_id)
        .scalar()
    ) or Decimal('0.0000')


# This can be stored somewhere secure and brought into memory
# Need a rotation strategy
SECRET = binascii.unhexlify('5dc7f099a5364124aa299ec35a622eb3')


def encrypt_pin(pin, salt):
    passw = (pin + str(salt)).encode('utf8')
    key = pbkdf2_hmac('sha256', passw, SECRET, 100000, 32)

    return binascii.hexlify(key).decode('utf8')

from decimal import Decimal
from flask import g
from bank.models import Exchange
from bank.db import db


def get_balance(account_id):
    return (
        db.session.query(db.func.SUM(Exchange.amount))
        .filter(Exchange.account_id == g.session.account_id)
        .scalar()
    ) or Decimal('0.0000')

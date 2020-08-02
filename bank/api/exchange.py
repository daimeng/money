from datetime import datetime
from decimal import Decimal
from flask import Blueprint, jsonify, request, g

from bank import utils
from bank.models import Exchange
from bank.db import db

exchange_bp = Blueprint('exchange', __name__)


@exchange_bp.route('/deposit/<amount>', methods=['POST'])
def deposit(amount):
    # Parse
    amount = Decimal(amount)
    account_id = g.session.account_id

    # CREATE new exchange
    exchange = Exchange(account_id=account_id, amount=amount, party='ATM')
    db.session.add(exchange)
    db.session.commit()

    balance = utils.get_balance(account_id)

    return jsonify({'balance': str(balance)}), 200


OVERDRAFT_FEE = Decimal('5.00')


@exchange_bp.route('/withdraw/<amount>', methods=['POST'])
def withdraw(amount):
    # Parse
    amount = Decimal(amount)
    account_id = g.session.account_id

    # CREATE new exchange
    exchange = Exchange(account_id=account_id, amount=-amount, party='ATM')
    db.session.add(exchange)

    balance = utils.get_balance(account_id)

    # Overdrawn path
    if balance < -amount:
        db.session.rollback()
        return jsonify({'reason': 'Overdrawn'}), 409

    # Overdraft path
    if balance < 0:
        overdraft = Exchange(account_id=account_id, amount=-OVERDRAFT_FEE, party='BANK')
        db.session.add(overdraft)
        db.session.commit()

        return (
            jsonify(
                {
                    'balance': str(balance + overdraft.amount),
                    'overdraft': str(-overdraft.amount),
                }
            ),
            200,
        )

    db.session.commit()
    return jsonify({'balance': str(balance)}), 200

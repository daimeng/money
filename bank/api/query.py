from flask import Blueprint, jsonify, request, g
from bank.models import Exchange
from bank import utils
from bank.db import db

query_bp = Blueprint('query', __name__)


@query_bp.route('/balance', methods=['GET'])
def get_balance():
    balance = utils.get_balance(g.session.account_id)

    return jsonify({'balance': str(balance)})


@query_bp.route('/history', methods=['GET'])
def get_history():
    res = (
        db.session.query(
            Exchange,
            db.func.sum(Exchange.amount)
            .over(partition_by=Exchange.account_id, order_by=Exchange.created_at.asc())
            .label('balance'),
        )
        .filter(Exchange.account_id == g.session.account_id)
        .all()
    )

    return jsonify(
        [
            {
                'amount': str(entry.amount),
                'party': entry.party,
                'created_at': int(entry.created_at.timestamp()),
                'balance': str(balance),
            }
            for entry, balance in res
        ]
    )

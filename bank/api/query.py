from flask import Blueprint, jsonify, request, g
from bank.models import Exchange
from bank import utils

query_bp = Blueprint('query', __name__)


@query_bp.route('/balance', methods=['GET'])
def get_balance():
    balance = utils.get_balance(g.session.account_id)

    return jsonify({'balance': str(balance)})


@query_bp.route('/history', methods=['GET'])
def get_history():
    res = Exchange.query.filter(Exchange.account_id == g.session.account_id).all()

    return jsonify(
        [
            {
                'amount': str(entry.amount),
                'party': entry.party,
                'created_at': int(entry.created_at.timestamp()),
            }
            for entry in res
        ]
    )

import logging
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from bank.models import Account, Session
from bank.db import db

auth_bp = Blueprint('auth', __name__)

logger = logging.getLogger(__name__)

EXPIRY = timedelta(minutes=2)


@auth_bp.route('/authorize', methods=['POST'])
def authorize():
    auth = request.authorization
    if not auth:
        return jsonify({'reason': 'AuthMissing'}), 400

    # CHECK creds
    account = Account.query.filter(
        Account.account_id == auth.username, Account.pin == auth.password
    ).one_or_none()
    if not account:
        return jsonify({'reason': 'Unauthorized'}), 401

    # CHECK existing session
    session = Session.query.filter(
        Session.account_id == account.id, Session.expires_at > datetime.utcnow()
    ).first()

    if session:
        return (
            jsonify(
                {
                    'token': session.token,
                    'expires_at': int(session.expires_at.timestamp()),
                }
            ),
            200,
        )

    # CREATE new session
    token = secrets.token_urlsafe()
    expires_at = datetime.utcnow() + EXPIRY
    session = Session(token=token, account_id=account.id, expires_at=expires_at)
    db.session.add(session)
    db.session.commit()

    return jsonify({'token': token, 'expires_at': int(expires_at.timestamp())}), 201


@auth_bp.route('/logout/<token>', methods=['POST'])
def logout(token):
    # CHECK for existing session
    session = Session.query.filter(Session.token == token).first()
    if not session:
        return jsonify({'reason': 'SessionNotFound'}), 404

    # DELETE and return
    db.session.delete(session)
    db.session.commit()
    return jsonify({}), 200


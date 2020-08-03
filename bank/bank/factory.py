import csv
import os
from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from flask import Flask, request, g, jsonify

from bank.api.exchange import exchange_bp
from bank.api.query import query_bp
from bank.api.auth import auth_bp
from bank.models import Account, Exchange, Session
from bank.utils import encrypt_pin
from bank.db import db


DB_URL = 'postgresql+psycopg2://{user}:{password}@{url}/{dbname}'.format(
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    url=os.getenv('POSTGRES_URL'),
    dbname=os.getenv('POSTGRES_DB'),
)


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    app.register_blueprint(query_bp)
    app.register_blueprint(exchange_bp)
    app.register_blueprint(auth_bp)

    # Request hooks
    @app.before_request
    def auth_check():
        # SKIP token auth step for auth related endpoints
        if not request.endpoint or request.endpoint.startswith('auth'):
            return

        # CHECK auth header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'reason': 'AuthMissing'}), 401

        *_, token = auth_header.split(' ')

        # CHECK for existing session
        session = Session.query.filter(
            Session.token == token, Session.expires_at > datetime.utcnow()
        ).first()
        if not session:
            return jsonify({'reason': 'Unauthorized'}), 401

        g.session = session

    # custom "flask <command>"s
    @app.cli.command('initdb')
    def initdb():
        db.create_all()

    @app.cli.command('load-state')
    def load_state():
        with open('state.csv', 'r') as f:
            reader = csv.reader(f, delimiter=',')
            header = next(reader)
            for row in reader:
                data = dict(zip(header, row))
                salt = uuid4()
                account = Account(
                    account_id=data['ACCOUNT_ID'],
                    pin_encrypted=encrypt_pin(data['PIN'], salt),
                    salt=salt,
                )
                db.session.add(account)
                db.session.flush()  # flush for id

                balance = Decimal(data['BALANCE'])
                if balance:
                    exchange = Exchange(
                        account_id=account.id, amount=balance, party='BANK'
                    )
                    db.session.add(exchange)
                db.session.commit()

    return app

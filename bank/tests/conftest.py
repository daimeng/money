import base64
import os
import pytest
import testing.postgresql
from uuid import uuid4
from sqlalchemy import create_engine

from bank.factory import create_app, db as _db
from bank.utils import encrypt_pin
from bank.models import Account


@pytest.fixture(scope='session')
def app():
    _app = create_app()
    with testing.postgresql.Postgresql() as postgresql:
        database_url = postgresql.url()
        _app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        _app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}

        yield _app


@pytest.fixture(scope='function')
def app_context(app):
    with app.app_context() as ctx:
        yield ctx


@pytest.fixture(scope='session')
def db(app):
    _db.app = app
    _db.create_all()
    yield _db
    _db.session.close()


@pytest.fixture(scope='function')
def session(db):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = db.create_scoped_session(options=options)

    db.session = session_
    db.Model.query = db.session.query_property()

    yield session_

    transaction.rollback()

    connection.close()
    session_.remove()


# Default test account
@pytest.fixture(scope='function')
def account(session):
    salt = uuid4()
    acc = Account(
        account_id='1234567890', pin_encrypted=encrypt_pin('1234', salt), salt=salt
    )
    session.add(acc)
    session.commit()


@pytest.fixture(scope='function')
def client(app, account):
    client = app.test_client()
    authstring = base64.b64encode(b'1234567890:1234').decode('utf-8')
    client.environ_base['HTTP_AUTHORIZATION'] = f'Basic {authstring}'
    return client


@pytest.fixture(scope='function')
def authed_client(app, client):
    res = client.post('/authorize')
    print(res.json)
    token = res.json['token']
    authed = app.test_client()
    authed.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'

    return authed

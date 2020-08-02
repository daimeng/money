import base64
from datetime import datetime, timedelta
from bank.models import Account


def test_authorize_bad_request(app):
    res = app.test_client().post('/authorize')
    assert res.status_code == 400
    assert res.json == {'reason': 'AuthMissing'}


def test_authorize_pin_fail(app, db):
    # Real account, bad pin
    client = app.test_client()
    authstring = base64.b64encode(b'1234567890:4321').decode('utf-8')
    client.environ_base['HTTP_AUTHORIZATION'] = f'Basic {authstring}'
    res = client.post('/authorize')
    assert res.status_code == 401
    assert res.json == {'reason': 'Unauthorized'}


def test_authorize_account_fail(app, db):
    # Fake account
    client = app.test_client()
    authstring = base64.b64encode(b'1234567899:1234').decode('utf-8')
    client.environ_base['HTTP_AUTHORIZATION'] = f'Basic {authstring}'
    res = client.post('/authorize')
    assert res.status_code == 401
    assert res.json == {'reason': 'Unauthorized'}


def test_authorize(client):
    now = datetime.utcnow()
    res = client.post('/authorize')
    assert res.status_code == 201
    expires_at = res.json['expires_at']
    assert expires_at < (now + timedelta(minutes=2.1)).timestamp()
    assert len(res.json['token']) == 43

    res = client.post('/authorize')
    assert res.status_code == 200
    assert res.json['expires_at'] == expires_at


def test_logout_expire(client, freezer):
    res = client.post('/authorize')
    assert res.status_code == 201
    freezer.move_to(datetime.utcnow() + timedelta(minutes=2.1))

    # Check expiry
    res = client.get('/balance')
    assert res.status_code == 401
    assert res.json == {'reason': 'Unauthorized'}

    # Check new session created
    res = client.post('/authorize')
    assert res.status_code == 201


def test_logout(client):
    res = client.post('/authorize')
    assert res.status_code == 201
    token = res.json['token']

    res = client.post(f'/logout/{token}')
    assert res.status_code == 200
    assert res.json == {}

    # Check double logout
    res = client.post(f'/logout/{token}')
    assert res.status_code == 404
    assert res.json == {'reason': 'SessionNotFound'}

    # Check unauth
    res = client.get('/balance')
    assert res.status_code == 401
    assert res.json == {'reason': 'Unauthorized'}

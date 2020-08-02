from datetime import datetime, timedelta


def test_balance_empty(authed_client):
    res = authed_client.get('/balance')
    assert res.status_code == 200
    assert res.json == {'balance': '0.0000'}


def test_history_empty(authed_client):
    res = authed_client.get('/history')
    assert res.status_code == 200
    assert res.json == []


def test_history_balance_overdraft(authed_client, freezer):
    now = int(datetime.utcnow().timestamp())
    authed_client.post('/deposit/1.0000')
    authed_client.post('/withdraw/2.0000')
    authed_client.post('/deposit/3.0000')

    res = authed_client.get('/balance')
    assert res.status_code == 200
    assert res.json == {'balance': '-3.0000'}

    res = authed_client.get('/history')
    assert res.status_code == 200
    assert res.json == [
        {'amount': '1.0000', 'created_at': now, 'party': 'ATM', 'balance': '1.0000'},
        {'amount': '-2.0000', 'created_at': now, 'party': 'ATM', 'balance': '-1.0000'},
        {'amount': '-5.0000', 'created_at': now, 'party': 'BANK', 'balance': '-6.0000'},
        {'amount': '3.0000', 'created_at': now, 'party': 'ATM', 'balance': '-3.0000'},
    ]

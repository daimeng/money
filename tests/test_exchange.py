def test_deposit(authed_client):
    res = authed_client.post('/deposit/500.12')
    assert res.status_code == 200
    assert res.json == {'balance': '500.1200'}


def test_withdraw_overdraw_paths(authed_client):
    res = authed_client.post('/withdraw/1.23')
    assert res.status_code == 200
    assert res.json == {'balance': '-6.2300', 'overdraft': '5.0000'}

    res = authed_client.post('/withdraw/1.23')
    assert res.status_code == 409
    assert res.json == {'reason': 'Overdrawn'}

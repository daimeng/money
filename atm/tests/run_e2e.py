from decimal import Decimal
from uuid import uuid4

from atm.run import process_entry
from atm.utils import ANY_SPACE

# ACCOUNT_ID,PIN,BALANCE
# 2859459814,7386,10.24
# 1434597300,4557,90000.55
# 7089382418,0075,0.00
# 2001377812,5950,60.00


def test_process_simple(capsys):
    # simple flow
    process_entry('authorize 7089382418 0075')
    assert capsys.readouterr().out == '7089382418 successfully authorized.\n'

    process_entry('balance')
    assert capsys.readouterr().out == 'Current balance:                0.00\n'

    process_entry('history')
    assert capsys.readouterr().out == 'No history found.\n'

    end = process_entry('logout')
    assert end is None
    assert capsys.readouterr().out == 'Account 7089382418 logged out.\n'


def test_process_auth_fail(capsys):
    process_entry('authorize 7089382418 0000')
    assert capsys.readouterr().out == 'Authorization failed.\n'


def test_process_unauth(capsys):
    for entry in ['deposit 20', 'withdraw 20', 'balance', 'history']:
        process_entry(entry)
        assert capsys.readouterr().out == 'Authorization required.\n'


def test_process_logout_fail(capsys):
    process_entry('logout')
    assert capsys.readouterr().out == 'No account is currently authorized.\n'


def test_process_full_flow(capsys):
    process_entry('authorize 2001377812 5950')
    assert capsys.readouterr().out == '2001377812 successfully authorized.\n'

    # test bad amount
    process_entry('withdraw 10')
    assert capsys.readouterr().out == 'Withdrawal amount must be multiple of 20.\n'

    process_entry('withdraw 60')
    assert (
        capsys.readouterr().out
        == """Amount dispensed: $           60
Current balance:                0.00
"""
    )

    process_entry('withdraw 20')
    assert (
        capsys.readouterr().out
        == """Amount dispensed: $           20
You have been charged an overdraft fee of 5.00$.
Current balance:              -25.00
"""
    )

    process_entry('withdraw 20')
    assert (
        capsys.readouterr().out
        == 'Your account is overdrawn! You may not make withdrawals at this time.\n'
    )

    process_entry('deposit 40')
    assert capsys.readouterr().out == 'Current balance:               15.00\n'

    process_entry('balance')
    assert capsys.readouterr().out == 'Current balance:               15.00\n'

    process_entry('history')
    lines = capsys.readouterr().out.split('\n')
    parsed = [ANY_SPACE.split(line.strip()) for line in lines]
    assert parsed[0] == ['DATE', 'TIME', 'AMOUNT', 'BALANCE']
    assert [line[2:] for line in parsed[1:]] == [
        ['60.00', '60.00'],
        ['-60.00', '0.00'],
        ['-20.00', '-20.00'],
        ['-5.00', '-25.00'],
        ['40.00', '15.00'],
        [],
    ]
    # Example:
    #       DATE     TIME        AMOUNT             BALANCE
    # 2020-08-02 21:58:35         60.00               60.00
    # 2020-08-02 21:58:38        -60.00                0.00
    # 2020-08-02 21:58:38        -20.00              -20.00
    # 2020-08-02 21:58:38         -5.00              -25.00
    # 2020-08-02 21:58:38         40.00               15.00

    # test end flow
    end = process_entry('end')
    assert end
    assert capsys.readouterr().out == 'Account 2001377812 logged out.\n'


def test_empty_atm(capsys):
    process_entry('authorize 1434597300 4557')
    assert capsys.readouterr().out == '1434597300 successfully authorized.\n'

    process_entry('withdraw 90000')
    lines = capsys.readouterr().out.split('\n')
    assert lines[0] == 'Unable to dispense full amount requested at this time.'
    assert Decimal(ANY_SPACE.split(lines[1])[3]) < 90000

    process_entry('withdraw 20')
    assert (
        capsys.readouterr().out == 'Unable to process your withdrawal at this time.\n'
    )

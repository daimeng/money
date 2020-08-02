import os
from decimal import Decimal
from datetime import datetime
from itertools import count

import requests

from atm.commands import VALID_COMMANDS

SESSION = {}
HOST = f"http://{os.getenv('BANK_HOST', 'localhost')}:{os.getenv('BANK_PORT', '5000')}"


def remote_call(method, path, **kwargs):
    url = f'{HOST}/{path}'
    if not SESSION:
        return requests.request(
            method, url, headers={'Content-Type': 'application/json'}, **kwargs
        )

    return requests.request(
        method,
        url,
        headers={
            'Authorization': f"Bearer {SESSION['token']}",
            'Content-Type': 'application/json',
        },
        **kwargs,
    )


def check_auth(cmd):
    if not SESSION:
        if cmd not in {'authorize', 'logout', 'end', 'help', ''}:
            return 'Authorization required.'


def process_cmd(cmd, args, session=SESSION):
    account_id = session.get('account_id')
    token = session.get('token')

    # Session management commands
    if cmd == 'authorize':
        res = remote_call('POST', 'authorize', auth=(args['account_id'], args['pin']))
        if res.ok:
            data = res.json()
            session['account_id'] = args['account_id']
            session['token'] = data['token']
            print(f"{args['account_id']} successfully authorized.")
        else:
            print('Authorization failed.')

    elif cmd == 'logout':
        # Nothing to do
        if account_id is None:
            print('No account is currently authorized.')
            return

        res = remote_call('POST', f'logout/{token}')
        if res.ok:
            print(f'Account {account_id} logged out.')
        elif res.status_code == 404:
            print(f'Session expired.')

        # Always clear vars
        session.clear()

    elif cmd == 'end':
        # logout first if active session
        if session:
            res = remote_call('POST', f'logout/{token}')
            if res.ok:
                print(f'Account {account_id} logged out.')
        return True

    elif cmd == 'help':
        for k, v in VALID_COMMANDS.items():
            print(k, ' '.join(f'<{vv}>' for vv in v))

    # Account actions
    elif cmd == 'withdraw':
        value = Decimal(args['value'])

        if value % 20 != 0:
            print(f'Withdrawal amount must be multiple of 20.')
            return

        res = remote_call('POST', f'withdraw/{value}')
        if res.ok:
            data = res.json()
            print(f"Amount dispensed: ${value:13.0f}")
            overdraft = Decimal(data.get('overdraft'))
            if overdraft:
                print(f"You have been charged an overdraft fee of {overdraft:.2f}$.")
            print(f"Current balance: {Decimal(data['balance']):19.2f}")
        elif res.status_code == 409:
            print(
                'Your account is overdrawn! You may not make withdrawals at this time.'
            )

    elif cmd == 'deposit':
        value = Decimal(args['value'])
        res = remote_call('POST', f'deposit/{value}')
        if res.ok:
            data = res.json()
            print(f"Current balance: {Decimal(data['balance']):19.2f}")

    elif cmd == 'balance':
        res = remote_call('GET', 'balance')
        if res.ok:
            data = res.json()
            print(f"Current balance: {Decimal(data['balance']):19.2f}")

    elif cmd == 'history':
        res = remote_call('GET', 'history')
        if res.ok:
            data = res.json()
            if not data:
                print('No history found.')
            else:
                print(
                    'DATE'.rjust(10),
                    'TIME'.rjust(8),
                    'AMOUNT'.rjust(13),
                    'BALANCE'.rjust(19),
                )
                for row in data:
                    dt = datetime.fromtimestamp(row['created_at'])
                    print(
                        dt.date(),
                        dt.time(),
                        '{:13.2f}'.format(Decimal(row['amount'])),
                        '{:19.2f}'.format(Decimal(row['balance'])),
                    )

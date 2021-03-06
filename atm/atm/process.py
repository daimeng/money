import os
import os
import glob

from decimal import Decimal
from datetime import datetime
from itertools import count

import requests

from atm.commands import VALID_COMMANDS
from atm.utils import bill_count, dispense_bills

# Bank host
HOST = f"http://{os.getenv('BANK_HOST', 'localhost')}:{os.getenv('BANK_PORT', '5000')}"

# Global session
SESSION = {}


def remote_call(method, path, **kwargs):
    """Wrapper around requests to call bank endpoints"""

    url = f'{HOST}/{path}'
    if not SESSION:
        return requests.request(
            method, url, headers={'Content-Type': 'application/json'}, **kwargs
        )

    resp = requests.request(
        method,
        url,
        headers={
            'Authorization': f"Bearer {SESSION['token']}",
            'Content-Type': 'application/json',
        },
        **kwargs,
    )

    if resp.status_code == 401:
        print('Session expired.')
        SESSION.clear()

    return resp


def check_auth(cmd):
    """Check if command requires authenticated session."""

    if not SESSION:
        if cmd not in {'authorize', 'logout', 'end', 'help', ''}:
            return 'Authorization required.'


def process_cmd(cmd, args):
    """
    Process a cmd string with arg dictionary.
    Returns True if process should terminate.
    """
    account_id = SESSION.get('account_id')
    token = SESSION.get('token')

    #############################
    # Session management commands
    #############################
    if 'authorize' == cmd:
        # Basic auth call, send over account id and pin.
        # Can use public private key pair and TLS for a bit more security.
        res = remote_call('POST', 'authorize', auth=(args['account_id'], args['pin']))

        # Successfully received token from server
        # Set global session
        if res.ok:
            data = res.json()
            SESSION['account_id'] = args['account_id']
            SESSION['token'] = data['token']
            print(f"{args['account_id']} successfully authorized.")
        else:
            print('Authorization failed.')

    elif 'logout' == cmd:
        # Nothing to do
        if account_id is None:
            print('No account is currently authorized.')
            return

        # Logout session on server
        res = remote_call('POST', f'logout/{token}')
        if res.ok:
            print(f'Account {account_id} logged out.')

        # May be already expired
        elif res.status_code == 404:
            print(f'Session expired.')

        # Always clear vars
        SESSION.clear()

    elif 'end' == cmd:
        # logout first if active session
        if SESSION:
            res = remote_call('POST', f'logout/{token}')
            if res.ok:
                print(f'Account {account_id} logged out.')
        return True

    elif 'help' == cmd:
        for k, v in VALID_COMMANDS.items():
            print(k, ' '.join(f'<{vv}>' for vv in v))

    ############################
    # Account actions
    ############################
    elif 'withdraw' == cmd:
        value = args['value']

        # Machine only contains 20 dollar bills
        if value % 20:
            print(f'Withdrawal amount must be multiple of 20.')
            return

        # CHECK if inventory is sufficient
        bills_required = int(value / 20)
        current_bill_count = bill_count()
        if current_bill_count == 0:
            print('Unable to process your withdrawal at this time.')
            return

        # IF not enough, adjust down amount with warning
        if current_bill_count < bills_required:
            bills_required = current_bill_count
            value = bills_required * Decimal(20)
            print('Unable to dispense full amount requested at this time.')

        # Make withdrawal call to bank
        res = remote_call('POST', f'withdraw/{value}')
        if res.ok:
            data = res.json()
            print(f"Amount dispensed: ${value:13.0f}")

            # Successful request can cause overdraft
            overdraft = data.get('overdraft')
            if overdraft:
                print(
                    f"You have been charged an overdraft fee of {Decimal(overdraft):.2f}$."
                )
            print(f"Current balance: {Decimal(data['balance']):19.2f}")

            # Dispense bills from inventory
            dispense_bills(bills_required)

        # CHECK overdrawn
        elif res.status_code == 409:
            print(
                'Your account is overdrawn! You may not make withdrawals at this time.'
            )

    elif 'deposit' == cmd:
        value = args['value']
        res = remote_call('POST', f'deposit/{value}')
        if res.ok:
            data = res.json()
            print(f"Current balance: {Decimal(data['balance']):19.2f}")

    elif 'balance' == cmd:
        res = remote_call('GET', 'balance')
        if res.ok:
            data = res.json()
            print(f"Current balance: {Decimal(data['balance']):19.2f}")

    elif 'history' == cmd:
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

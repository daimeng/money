import regex
import requests
from datetime import datetime
from decimal import Decimal
from itertools import count
from pprint import pprint

from prompt_toolkit.validation import Validator, ValidationError

from PyInquirer import prompt


VALID_COMMANDS = {
    'authorize': ['account_id', 'pin'],
    'withdraw': ['value'],
    'deposit': ['value'],
    'balance': [],
    'history': [],
    'logout': [],
    'end': [],
    'help': [],
}

ACCOUNT_ID = None
TOKEN = None
HOST = 'http://localhost:5000'


def remote_call(method, path, **kwargs):
    url = f'{HOST}/{path}'
    if TOKEN is None:
        return requests.request(
            method, url, headers={'Content-Type': 'application/json'}, **kwargs
        )

    return requests.request(
        method,
        url,
        headers={
            'Authorization': f'Bearer {TOKEN}',
            'Content-Type': 'application/json',
        },
        **kwargs,
    )


console = [{'type': 'input', 'name': 'cmd', 'message': '>'}]

while True:
    entry = prompt(console)

    # Parsing command
    cmd, *vargs = (x.strip() for x in entry['cmd'].strip().split(' '))
    if cmd not in VALID_COMMANDS:
        print(f'Invalid command "{cmd}".')
        continue

    if len(vargs) != len(VALID_COMMANDS[cmd]):
        print('Missing arguments.')
        continue

    args = dict(zip(VALID_COMMANDS[cmd], vargs))

    # Auth gate account actions
    if ACCOUNT_ID is None:
        if cmd not in {'authorize', 'logout', 'end', 'help', ''}:
            print('Authorization required.')
            continue

    # Session management commands
    if cmd == 'authorize':
        res = remote_call('POST', 'authorize', auth=(args['account_id'], args['pin']))
        if res.ok:
            data = res.json()
            ACCOUNT_ID = args['account_id']
            TOKEN = data['token']
            print(f"{args['account_id']} successfully authorized.")
        else:
            print('Authorization failed.')

    elif cmd == 'logout':
        # Nothing to do
        if ACCOUNT_ID is None:
            print('No account is currently authorized.')
            continue

        res = remote_call('POST', f'logout/{TOKEN}')
        if res.ok:
            print(f'Account {ACCOUNT_ID} logged out.')
        elif res.status_code == 404:
            print(f'Session expired.')

        # Always clear vars
        ACCOUNT_ID = None
        TOKEN = None

    elif cmd == 'end':
        # logout first if active session
        if ACCOUNT_ID is not None:
            res = remote_call('POST', f'logout/{TOKEN}')
            if res.ok:
                print(f'Account {ACCOUNT_ID} logged out.')
        break

    elif cmd == 'help':
        for k, v in VALID_COMMANDS.items():
            print(k, ' '.join(f'<{vv}>' for vv in v))

    # Account actions
    elif cmd == 'withdraw':
        value = int(args['value'])
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
        value = int(args['value'])
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
                for row in data:
                    dt = datetime.fromtimestamp(row['created_at'])
                    print(
                        dt.date(),
                        dt.time(),
                        '{:13.2f}'.format(Decimal(row['amount'])),
                        '{:19.2f}'.format(Decimal(row['balance'])),
                    )

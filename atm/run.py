import requests
from datetime import datetime
from decimal import Decimal
from itertools import count

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


def parse_entry(entry, command_list=VALID_COMMANDS):
    # Parsing command
    cmd, *vargs = entry['cmd'].strip().split(' ')
    if cmd not in command_list:
        return f'Invalid command "{cmd}".', None, None

    arg_list = command_list[cmd]
    if len(vargs) != len(arg_list):
        return f"Usage: {cmd} {' '.join(f'<{v}>' for v in arg_list)}", None, None

    args = dict(zip(arg_list, vargs))

    return None, cmd, args


while True:
    entry = prompt(console)

    error, cmd, args = parse_entry(entry)
    if error:
        print(error)
        continue

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
        value = Decimal(args['value'])

        if value % 20 != 0:
            print(f'Withdrawal amount must be multiple of 20.')
            continue

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

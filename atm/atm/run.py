import os
import requests
from datetime import datetime
from decimal import Decimal
from itertools import count

from PyInquirer import prompt

from atm.commands import VALID_COMMANDS
from atm.utils import parse_entry
from atm.process import check_auth, process_cmd


console = [{'type': 'input', 'name': 'cmd', 'message': '>'}]


while True:
    entry = prompt(console)

    error, cmd, args = parse_entry(entry, command_list=VALID_COMMANDS)
    if error:
        print(error)
        continue

    # Auth gate account actions
    error = check_auth(cmd)
    if error:
        print(error)
        continue

    # Process command
    end = process_cmd(cmd, args)
    if end:
        break

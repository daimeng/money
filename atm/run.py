import regex
from itertools import count
from pprint import pprint

from prompt_toolkit.validation import Validator, ValidationError

from PyInquirer import prompt


VALID_COMMANDS = {
    'authorize',
    'withdraw',
    'deposit',
    'balance',
    'history',
    'logout',
    'end',
}


def validate_command(input):

    return True


console = [
    {'type': 'input', 'name': 'command', 'message': '>', 'validate': validate_command}
]

while True:
    command = prompt(console)
    pprint(command)

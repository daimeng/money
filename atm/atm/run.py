from PyInquirer import prompt

from atm.commands import VALID_COMMANDS
from atm.utils import parse_entry
from atm.process import check_auth, process_cmd


console = [{'type': 'input', 'name': 'cmd', 'message': '>'}]


def main():
    while True:
        entry = prompt(console)
        if process_entry(entry['cmd']):
            break


def process_entry(entry):
    # Validate user input
    error, cmd, args = parse_entry(entry, command_list=VALID_COMMANDS)
    if error:
        print(error)
        return

    # Auth gate account actions
    error = check_auth(cmd)
    if error:
        print(error)
        return

    # Process command
    return process_cmd(cmd, args)


if __name__ == "__main__":
    main()

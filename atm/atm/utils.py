import re
import os
import glob
import decimal


ANY_SPACE = re.compile(r'\s+')


def parse_entry(entry, command_list):
    # Parsing command
    cmd, *vargs = ANY_SPACE.split(entry.strip())
    if cmd not in command_list:
        return f'Invalid command "{cmd}".', None, None

    arg_list = command_list[cmd]
    if len(vargs) != len(arg_list):
        return f"Usage: {cmd} {' '.join(f'<{v}>' for v in arg_list)}", None, None

    args = dict(zip(arg_list, vargs))

    if 'value' in args:
        try:
            args['value'] = decimal.Decimal(args['value'])
        except decimal.InvalidOperation:
            return f"Invalid amount: {args['value']}.", None, None

        if args['value'] <= 0:
            return f"Invalid amount: {args['value']}.", None, None

    return None, cmd, args


def bill_count():
    return len(glob.glob('cashbox/*.twenty'))


def dispense_bills(count):
    dispensed = 0
    for f in glob.glob('cashbox/*.twenty')[:count]:
        os.remove(f)
        dispensed += 1

    return dispensed

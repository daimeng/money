import re


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

    return None, cmd, args

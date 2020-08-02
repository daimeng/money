def parse_entry(entry, command_list):
    # Parsing command
    cmd, *vargs = entry['cmd'].strip().split(' ')
    if cmd not in command_list:
        return f'Invalid command "{cmd}".', None, None

    arg_list = command_list[cmd]
    if len(vargs) != len(arg_list):
        return f"Usage: {cmd} {' '.join(f'<{v}>' for v in arg_list)}", None, None

    args = dict(zip(arg_list, vargs))

    return None, cmd, args

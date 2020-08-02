from atm.utils import parse_entry

TEST_COMMANDS = {'foo': [], 'bar': ['test', 'baz']}


def test_parse_empty():
    res = parse_entry({'cmd': ''}, command_list=TEST_COMMANDS)
    assert res == ('Invalid command "".', None, None)


def test_parse_foo():
    res = parse_entry({'cmd': 'foo'}, command_list=TEST_COMMANDS)
    assert res == (None, 'foo', {})


def test_parse_spaces():
    res = parse_entry({'cmd': 'foo '}, command_list=TEST_COMMANDS)
    assert res == (None, 'foo', {})

    res = parse_entry({'cmd': ' foo '}, command_list=TEST_COMMANDS)
    assert res == (None, 'foo', {})


def test_parse_bar():
    res = parse_entry({'cmd': 'bar a'}, command_list=TEST_COMMANDS)
    assert res == ('Usage: bar <test> <baz>', None, None)

    res = parse_entry({'cmd': 'bar a b'}, command_list=TEST_COMMANDS)
    assert res == (None, 'bar', {'test': 'a', 'baz': 'b'})

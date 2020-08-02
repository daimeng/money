from atm.run import process_entry


HELP_TEXT = """authorize <account_id> <pin>
withdraw <value>
deposit <value>
balance 
history 
logout 
end 
help 
"""


def test_help(capsys):
    res = process_entry('help')
    assert res == None
    assert capsys.readouterr().out == HELP_TEXT


def test_zero_amount(capsys):
    process_entry('deposit 0')
    assert capsys.readouterr().out == 'Invalid amount: 0.\n'

    process_entry('withdraw 0')
    assert capsys.readouterr().out == 'Invalid amount: 0.\n'


def test_negative_amount(capsys):
    process_entry('deposit -20')
    assert capsys.readouterr().out == 'Invalid amount: -20.\n'

    process_entry('withdraw -20')
    assert capsys.readouterr().out == 'Invalid amount: -20.\n'


def test_invalid_amount(capsys):
    process_entry('deposit x')
    assert capsys.readouterr().out == 'Invalid amount: x.\n'

    process_entry('withdraw x')
    assert capsys.readouterr().out == 'Invalid amount: x.\n'

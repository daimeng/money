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

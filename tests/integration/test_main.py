"""
"""

from zazo import main

def test_main(capsys):
    retval = main()

    assert retval == 0
    assert capsys.readouterr() == ("Hello World!\n", "")

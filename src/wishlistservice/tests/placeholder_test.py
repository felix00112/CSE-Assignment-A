# git only detects folders which have files in them so I added this placeholder
# remove / rename once we add actual functionality
# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


from placeholder import add, subtract


def test_add():
    assert add(3, 2) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_subtract():
    assert subtract(3, 2) == 1
    assert subtract(2, 3) == -1
    assert subtract(0, 0) == 0

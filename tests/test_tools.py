from app.tools import calculator,get_current_time

def test_calculator_add():
    assert calculator("2 + 3") == 5

def test_calculator_multiply():
    assert calculator("4 * 5") == 20


def test_get_current_time():
    assert isinstance(get_current_time(), str)

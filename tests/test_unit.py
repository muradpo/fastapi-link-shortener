from app.crud import generate_short_code


def test_generate_short_code_default_length():
    code = generate_short_code()
    assert isinstance(code, str)
    assert len(code) == 6


def test_generate_short_code_custom_length():
    code = generate_short_code(10)
    assert len(code) == 10


def test_generate_short_code_uniqueness():
    code1 = generate_short_code()
    code2 = generate_short_code()
    assert code1 != code2
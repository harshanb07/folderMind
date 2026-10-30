from src.foldermind.citations import validate_citations


def test_valid_reference():
    assert validate_citations(
        "Diameter is 24.95–25.05 mm [Source 1].", 3
    )


def test_nonexistent_reference():
    assert not validate_citations(
        "Diameter is 24.95–25.05 mm [Source 99].", 3
    )


def test_malformed_reference():
    assert not validate_citations(
        "The alarm occurred [Source N: machine.txt].", 3
    )


def test_missing_reference():
    assert not validate_citations(
        "The motor failed.", 3
    )


def test_another_invalid_reference():
    assert not validate_citations(
        "The Machine failed because of a spindle-stuck alarm [Source 5].",
        3
    )



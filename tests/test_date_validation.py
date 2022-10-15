import random
import re
from datetime import date

import pytest

from date_validation import (
    decrypt_date,
    encrypt_date,
    main,
    parse_date,
    random_chunks,
    shift_date,
)

TOKEN_PATTERN = re.compile(r"^[a-z]{9}\d{2}[a-z]{9}\d{2}[a-z]{9}\d{4}$")


@pytest.mark.parametrize("value", [
    date(2024, 12, 29),
    date(2024, 1, 5),
    date(2024, 11, 1),   # used to decrypt as 1224-01-01
    date(2020, 5, 5),    # year ending in 0 used to crash
    date(2101, 2, 28),   # reversed year 1012
    date(2024, 2, 29),
    date(1999, 12, 31),
])
@pytest.mark.parametrize("key", [0, 1, 7, 42])
def test_round_trip(value, key):
    token = encrypt_date(value, key)
    assert decrypt_date(token, key) == value


def test_year_with_small_reversed_value():
    # 2100 reversed is 0012 -> 12; encoded as 4 zero-padded digits
    token = encrypt_date("2100-02-28", 7)
    assert re.sub(r"\D", "", token) == "35090005"
    assert decrypt_date(token, 7) == date(2100, 2, 28)


def test_known_example_matches_original_scheme():
    # 2024-12-29, key 7 -> day 36, month 19, reversed year 4202 - 7 = 4195
    assert shift_date(date(2024, 12, 29), 7) == ["36", "19", "4195"]


def test_token_shape():
    token = encrypt_date("2024-12-29", 7, rng=random.Random(1))
    assert TOKEN_PATTERN.match(token)
    assert re.sub(r"\D", "", token) == "36194195"


def test_seeded_rng_is_reproducible():
    assert encrypt_date("2024-12-29", 7, rng=random.Random(5)) == \
        encrypt_date("2024-12-29", 7, rng=random.Random(5))


def test_letters_are_ignored_on_decrypt():
    assert decrypt_date("AAA36--19..4195", 7) == date(2024, 12, 29)


def test_longer_noise_still_round_trips():
    token = encrypt_date("2024-12-29", 7, noise_length=40)
    assert decrypt_date(token, 7) == date(2024, 12, 29)


def test_wrong_key_does_not_return_original():
    token = encrypt_date("2024-12-29", 7)
    try:
        assert decrypt_date(token, 6) != date(2024, 12, 29)
    except ValueError:
        pass


@pytest.mark.parametrize("bad", ["2024-02-30", "2023-02-29", "2024-13-01", "29-12-2024", "", "not a date"])
def test_parse_date_rejects_invalid(bad):
    with pytest.raises(ValueError):
        parse_date(bad)


def test_encrypt_rejects_invalid_date_string():
    with pytest.raises(ValueError):
        encrypt_date("2024-02-30", 7)


def test_negative_key_rejected():
    with pytest.raises(ValueError):
        encrypt_date("2024-12-29", -1)
    with pytest.raises(ValueError):
        decrypt_date("x36x19x4195", -1)


def test_key_too_large_rejected():
    with pytest.raises(ValueError):
        encrypt_date("2024-12-31", 69)  # day 31 + 69 = 100, no longer 2 digits
    with pytest.raises(ValueError):
        encrypt_date("1000-01-01", 2)   # reversed year 1 - 2 < 0


def test_noise_too_short_rejected():
    with pytest.raises(ValueError):
        random_chunks(18)


@pytest.mark.parametrize("token", ["abc", "abc361941951", "x36x19x419"])
def test_decrypt_rejects_wrong_digit_count(token):
    with pytest.raises(ValueError):
        decrypt_date(token, 7)


def test_decrypt_rejects_impossible_date():
    with pytest.raises(ValueError):
        decrypt_date("x99x19x4195", 7)  # day 92


def test_cli_round_trip(capsys):
    assert main(["encrypt", "2024-12-29", "--key", "7"]) == 0
    token = capsys.readouterr().out.strip()
    assert main(["decrypt", token, "--key", "7"]) == 0
    assert capsys.readouterr().out.strip() == "2024-12-29"


def test_cli_reports_errors(capsys):
    assert main(["encrypt", "2024-02-30"]) == 1
    assert "invalid date" in capsys.readouterr().err

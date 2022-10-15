# Encryption-and-Decryption

A small Python script that turns a date into an obfuscated token and back, e.g.

```
2024-12-29  <->  hxbsrignd36rugfqxpyf19czzeecuhd4195
```

It was written to store an expiry/validation date for an offline app in a form
that is not readable at a glance.

> **Not real encryption.** This is a simple reversible shift cipher with random
> letters as padding. It only hides the date from casual inspection. Anyone with
> this code and a token can recover the date by trying the few possible keys.
> Do not use it to protect anything sensitive; use a vetted library (for example
> `cryptography`'s Fernet, or an HMAC signature if you only need tamper detection).

## How the scheme works

Given a date and a non-negative integer key `k`:

| Part  | Transformation                         | Width    | Example (2024-12-29, k = 7) |
|-------|----------------------------------------|----------|-----------------------------|
| day   | `day + k`                              | 2 digits | 29 + 7 = `36`               |
| month | `month + k`                            | 2 digits | 12 + 7 = `19`               |
| year  | reverse the 4-digit year, then `- k`   | 4 digits | 2024 -> 4202 - 7 = `4195`   |

Each of the three numbers is preceded by a chunk of 9 random lowercase letters
(27 letters by default), giving `<9 letters>DD<9 letters>MM<9 letters>YYYY`.

Decryption ignores every non-digit character, reads the 8 digits as
`DD MM YYYY`, reverses the arithmetic and checks that the result is a real
calendar date. Because the letters are random, encrypting the same date twice
gives different tokens that decrypt to the same date.

Limits: the key must keep `day + k` at two digits (`<= 99`) and
`reversed_year - k` non-negative. For example 2100 reverses to `0012`, so it
accepts keys 0-12 only. Out-of-range combinations are rejected with an error.

## Requirements

Python 3.8+ and the standard library only. `pytest` is needed to run the tests
(`requirements-dev.txt`).

## Usage

```console
$ python date_validation.py encrypt 2024-12-29 --key 7
hxbsrignd36rugfqxpyf19czzeecuhd4195

$ python date_validation.py decrypt hxbsrignd36rugfqxpyf19czzeecuhd4195 --key 7
2024-12-29
```

A wrong key either fails or silently produces a different date, since there is
no integrity check:

```console
$ python date_validation.py decrypt hxbsrignd36rugfqxpyf19czzeecuhd4195 --key 3
error: token does not decode to a valid date with key 3

$ python date_validation.py decrypt hxbsrignd36rugfqxpyf19czzeecuhd4195 --key 8
3024-11-28
```

Invalid input dates are rejected:

```console
$ python date_validation.py encrypt 2024-02-30
error: invalid date '2024-02-30': expected a real date as YYYY-MM-DD
```

`--key` defaults to 7 and `encrypt --length` (default 27, minimum 19) sets how
many random letters are generated. Errors exit with status 1.

From Python:

```python
from datetime import date
from date_validation import encrypt_date, decrypt_date

token = encrypt_date(date(2024, 12, 29), key=7)
assert decrypt_date(token, key=7) == date(2024, 12, 29)
```

## Tests

```console
$ python -m venv .venv && . .venv/bin/activate
$ pip install -r requirements-dev.txt
$ pytest
```

The tests cover encrypt/decrypt round trips across many dates and keys,
the token format, invalid dates, out-of-range keys and malformed tokens.

## Changes from the original version

The algorithm is unchanged, but two bugs in the original class were fixed:

- Decryption did not zero-pad day and month before parsing, so some dates came
  back wrong (2024-11-01 decrypted as 1224-01-01).
- Years whose reversed value has fewer than four digits (e.g. 2020 -> 0202)
  produced a 3-digit field and decryption crashed. The year field is now always
  four zero-padded digits; tokens for every other year are identical to before.

## Author

Hanan Abbas

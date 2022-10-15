"""Obfuscate a date into a token of random letters and shifted digits, and back.

This is a simple reversible shift cipher with random-letter padding. It hides a
date from casual inspection; it is NOT cryptographically secure. Anyone who has
the code and a token can recover the key by trying the few possible values.

Scheme (key = small non-negative integer ``k``):

* day   -> ``day + k``                         as 2 digits
* month -> ``month + k``                       as 2 digits
* year  -> ``int(reversed 4-digit year) - k``  as 4 digits

Each of the three numbers is preceded by a chunk of 9 random lowercase letters.
Decryption strips every non-digit and reverses the arithmetic.
"""

from __future__ import annotations

import argparse
import random
import re
import string
import sys
import textwrap
from datetime import date

CHUNK_SIZE = 9
DEFAULT_NOISE_LENGTH = 27
MIN_NOISE_LENGTH = 2 * CHUNK_SIZE + 1  # enough letters for three chunks
DIGITS_LENGTH = 8  # DD + MM + YYYY


def parse_date(value: str) -> date:
    """Parse and validate an ISO date string (``YYYY-MM-DD``)."""
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid date {value!r}: expected a real date as YYYY-MM-DD") from exc


def _validate_key(key: int) -> None:
    if key < 0:
        raise ValueError("key must be a non-negative integer")


def random_chunks(length: int, rng: random.Random | None = None) -> list[str]:
    """Return ``length`` random lowercase letters split into chunks of 9."""
    if length < MIN_NOISE_LENGTH:
        raise ValueError(f"noise length must be at least {MIN_NOISE_LENGTH}")
    rng = rng or random.Random()
    letters = "".join(rng.choice(string.ascii_lowercase) for _ in range(length))
    return textwrap.wrap(letters, CHUNK_SIZE)


def shift_date(value: date, key: int) -> list[str]:
    """Apply the cipher arithmetic and return the three zero-padded fields."""
    _validate_key(key)
    reversed_year = int(f"{value.year:04d}"[::-1])
    day, month, year = value.day + key, value.month + key, reversed_year - key
    if day > 99 or month > 99 or year < 0:
        raise ValueError(f"key {key} is too large to encrypt {value.isoformat()}")
    return [f"{day:02d}", f"{month:02d}", f"{year:04d}"]


def encrypt_date(value: date | str, key: int,
                 noise_length: int = DEFAULT_NOISE_LENGTH,
                 rng: random.Random | None = None) -> str:
    """Encrypt ``value`` into a token such as ``abcdefghi36jklmnopqr19stuvwxyza4195``."""
    if isinstance(value, str):
        value = parse_date(value)
    fields = shift_date(value, key)
    chunks = random_chunks(noise_length, rng)
    return "".join(chunk + field for chunk, field in zip(chunks, fields))


def decrypt_date(token: str, key: int) -> date:
    """Recover the date from a token produced by :func:`encrypt_date`.

    Raises ``ValueError`` if the token does not decode to a real date.
    """
    _validate_key(key)
    digits = re.sub(r"\D", "", token)
    if len(digits) != DIGITS_LENGTH:
        raise ValueError(f"token must contain exactly {DIGITS_LENGTH} digits, got {len(digits)}")
    day = int(digits[0:2]) - key
    month = int(digits[2:4]) - key
    shifted_year = int(digits[4:8]) + key
    if shifted_year > 9999:
        raise ValueError(f"token does not decode to a valid date with key {key}")
    year = int(f"{shifted_year:04d}"[::-1])
    try:
        return date(year, month, day)
    except ValueError as exc:
        raise ValueError(f"token does not decode to a valid date with key {key}") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="date_validation.py",
        description="Obfuscate dates with a simple reversible shift cipher (not secure encryption).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    enc = sub.add_parser("encrypt", help="encrypt a YYYY-MM-DD date into a token")
    enc.add_argument("date", help="date in YYYY-MM-DD format")
    enc.add_argument("--key", type=int, default=7, help="shift key (default: 7)")
    enc.add_argument("--length", type=int, default=DEFAULT_NOISE_LENGTH,
                     help=f"number of random letters (default: {DEFAULT_NOISE_LENGTH})")

    dec = sub.add_parser("decrypt", help="decrypt a token back into a date")
    dec.add_argument("token", help="token produced by 'encrypt'")
    dec.add_argument("--key", type=int, default=7, help="shift key (default: 7)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "encrypt":
            print(encrypt_date(args.date, args.key, args.length))
        else:
            print(decrypt_date(args.token, args.key).isoformat())
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

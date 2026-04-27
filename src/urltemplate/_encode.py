"""Percent-encoding helpers for RFC 6570 expansion."""

from __future__ import annotations

UNRESERVED = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789-._~"
)

RESERVED = frozenset(":/?#[]@!$&'()*+,;=")

_HEX_DIGITS = "0123456789ABCDEF"


def _percent_encode_byte(byte: int) -> str:
    return "%" + _HEX_DIGITS[byte >> 4] + _HEX_DIGITS[byte & 0x0F]


def encode_unreserved(text: str) -> str:
    pieces = []
    for char in text:
        if char in UNRESERVED:
            pieces.append(char)
            continue
        for byte in char.encode("utf-8"):
            pieces.append(_percent_encode_byte(byte))
    return "".join(pieces)


def encode_reserved(text: str) -> str:
    pieces = []
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char in UNRESERVED or char in RESERVED:
            pieces.append(char); index += 1; continue
        if char == "%" and _is_pct_encoded_at(text, index):
            pieces.append(text[index : index + 3]); index += 3; continue
        for byte in char.encode("utf-8"):
            pieces.append(_percent_encode_byte(byte))
        index += 1
    return "".join(pieces)


def _is_pct_encoded_at(text, index):
    return (
        index + 2 < len(text)
        and text[index + 1] in _HEX_DIGITS_LOWER_OR_UPPER
        and text[index + 2] in _HEX_DIGITS_LOWER_OR_UPPER
    )


_HEX_DIGITS_LOWER_OR_UPPER = frozenset(_HEX_DIGITS + "abcdef")

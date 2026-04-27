"""Tests for percent-encoding helpers."""

from __future__ import annotations

from urltemplate import encode_reserved, encode_unreserved


def test_encode_unreserved_passes_unreserved_set_unchanged():
    text = "ABCabc012-._~"
    assert encode_unreserved(text) == text


def test_encode_unreserved_encodes_space_as_pct20():
    assert encode_unreserved("a b") == "a%20b"


def test_encode_unreserved_encodes_reserved_characters():
    assert encode_unreserved("/?#") == "%2F%3F%23"


def test_encode_unreserved_encodes_unicode_as_utf8():
    assert encode_unreserved("é") == "%C3%A9"


def test_encode_unreserved_encodes_multi_byte_emoji():
    assert encode_unreserved("😀") == "%F0%9F%98%80"


def test_encode_unreserved_uses_uppercase_hex():
    assert encode_unreserved("\xff") == "%C3%BF"


def test_encode_reserved_keeps_reserved_characters():
    text = ":/?#[]@!$&'()*+,;="
    assert encode_reserved(text) == text


def test_encode_reserved_keeps_existing_pct_encoded_triplets():
    assert encode_reserved("a%20b") == "a%20b"


def test_encode_reserved_keeps_pct_encoded_lowercase_triplet():
    assert encode_reserved("a%c3%a9b") == "a%c3%a9b"


def test_encode_reserved_encodes_naked_percent():
    assert encode_reserved("100%off") == "100%25off"


def test_encode_reserved_encodes_non_ascii():
    assert encode_reserved("café") == "caf%C3%A9"


def test_encode_reserved_encodes_space():
    assert encode_reserved("a b") == "a%20b"


def test_encode_unreserved_handles_empty_string():
    assert encode_unreserved("") == ""


def test_encode_reserved_handles_empty_string():
    assert encode_reserved("") == ""

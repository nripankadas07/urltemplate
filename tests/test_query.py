"""Tests for the level-3 ``?`` (form query) and ``&`` (form continuation) operators."""

from __future__ import annotations

import urltemplate


def test_query_emits_question_mark_prefix():
    assert urltemplate.expand("/x{?v}", {"v": "value"}) == "/x?v=value"


def test_query_empty_string_renders_with_equals():
    assert urltemplate.expand("/x{?v}", {"v": ""}) == "/x?v="


def test_query_undefined_variable_drops_with_no_question_mark():
    assert urltemplate.expand("/x{?v}", {}) == "/x"


def test_query_multi_variable_joins_with_ampersand():
    result = urltemplate.expand("/x{?a,b}", {"a": "1", "b": "2"})
    assert result == "/x?a=1&b=2"


def test_query_with_partially_undefined_variables():
    result = urltemplate.expand("/x{?a,b,c}", {"a": "1", "c": "3"})
    assert result == "/x?a=1&c=3"


def test_query_encodes_value_unreserved_only():
    assert urltemplate.expand("/x{?v}", {"v": "hello world"}) == "/x?v=hello%20world"


def test_query_with_integer_value():
    assert urltemplate.expand("/x{?page}", {"page": 7}) == "/x?page=7"


def test_query_list_value_joined_with_commas():
    result = urltemplate.expand("/x{?tags}", {"tags": ["python", "rfc6570"]})
    assert result == "/x?tags=python,rfc6570"


def test_query_dict_value_joined_with_commas():
    value = {"size": "large", "color": "red"}
    result = urltemplate.expand("/x{?opts}", {"opts": value})
    assert result == "/x?opts=size,large,color,red"


def test_query_empty_list_drops_expression():
    assert urltemplate.expand("/x{?tags}", {"tags": []}) == "/x"


def test_query_empty_dict_drops_expression():
    assert urltemplate.expand("/x{?opts}", {"opts": {}}) == "/x"


def test_query_all_variables_undefined_drops_question_mark():
    assert urltemplate.expand("/x{?a,b}", {}) == "/x"


def test_continuation_emits_ampersand_prefix():
    assert urltemplate.expand("/x?p=1{&v}", {"v": "value"}) == "/x?p=1&v=value"


def test_continuation_undefined_variable_drops_with_no_ampersand():
    assert urltemplate.expand("/x?p=1{&v}", {}) == "/x?p=1"


def test_continuation_multi_variable_joins_with_ampersand():
    result = urltemplate.expand("/x?p=1{&a,b}", {"a": "1", "b": "2"})
    assert result == "/x?p=1&a=1&b=2"


def test_continuation_with_list_value():
    result = urltemplate.expand("/x?p=1{&tags}", {"tags": ["a", "b", "c"]})
    assert result == "/x?p=1&tags=a,b,c"


def test_continuation_empty_string_renders_with_equals():
    assert urltemplate.expand("/x?p=1{&v}", {"v": ""}) == "/x?p=1&v="

"""Tests for composite (list / dict) values without explode."""

from __future__ import annotations

import urltemplate


def test_simple_with_list_uses_comma_separator():
    assert urltemplate.expand("/x/{v}", {"v": ["a", "b", "c"]}) == "/x/a,b,c"


def test_simple_with_dict_uses_comma_separator_kv_kv():
    value = {"k1": "v1", "k2": "v2"}
    assert urltemplate.expand("/x/{v}", {"v": value}) == "/x/k1,v1,k2,v2"


def test_simple_with_list_encodes_each_item_separately():
    assert urltemplate.expand("/x/{v}", {"v": ["a/b", "c d"]}) == "/x/a%2Fb,c%20d"


def test_reserved_with_list_keeps_reserved_chars():
    assert urltemplate.expand("/x/{+v}", {"v": ["a/b", "c?d"]}) == "/x/a/b,c?d"


def test_fragment_with_list_keeps_reserved_chars():
    assert urltemplate.expand("/x{#v}", {"v": ["a/b", "c?d"]}) == "/x#a/b,c?d"


def test_path_segment_with_list_no_explode():
    assert urltemplate.expand("/x{/v}", {"v": ["a", "b"]}) == "/x/a,b"


def test_label_with_list_no_explode():
    assert urltemplate.expand("X{.v}", {"v": ["a", "b"]}) == "X.a,b"


def test_query_with_list_uses_var_name_once():
    assert urltemplate.expand("/x{?tags}", {"tags": ["a", "b"]}) == "/x?tags=a,b"


def test_path_param_with_dict_renders_value_kv_pairs():
    value = {"size": "large"}
    assert urltemplate.expand("/x{;opts}", {"opts": value}) == "/x;opts=size,large"


def test_continuation_with_dict_renders_value_kv_pairs():
    value = {"size": "large", "color": "red"}
    result = urltemplate.expand("/x?z=1{&opts}", {"opts": value})
    assert result == "/x?z=1&opts=size,large,color,red"


def test_list_with_integer_items_renders_decimal():
    assert urltemplate.expand("/x{?v}", {"v": [1, 2, 3]}) == "/x?v=1,2,3"


def test_list_with_mixed_strings_and_ints():
    assert urltemplate.expand("/x/{v}", {"v": ["a", 7, "b"]}) == "/x/a,7,b"


def test_dict_with_integer_values():
    value = {"page": 7, "limit": 50}
    assert urltemplate.expand("/x{?p}", {"p": value}) == "/x?p=page,7,limit,50"


def test_dict_with_boolean_value_renders_lowercase():
    value = {"active": True}
    assert urltemplate.expand("/x{?p}", {"p": value}) == "/x?p=active,true"


def test_tuple_value_treated_like_list():
    assert urltemplate.expand("/x/{v}", {"v": ("a", "b")}) == "/x/a,b"


def test_empty_list_drops_for_simple_operator_too():
    assert urltemplate.expand("/x/{v}", {"v": []}) == "/x/"


def test_empty_dict_drops_for_simple_operator_too():
    assert urltemplate.expand("/x/{v}", {"v": {}}) == "/x/"

"""Tests focused on every documented error path."""

from __future__ import annotations

import pytest

import urltemplate


def test_template_syntax_error_is_subclass_of_uri_template_error():
    assert issubclass(urltemplate.TemplateSyntaxError, urltemplate.URITemplateError)


def test_expansion_error_is_subclass_of_uri_template_error():
    assert issubclass(urltemplate.ExpansionError, urltemplate.URITemplateError)


def test_expand_with_non_mapping_variables_raises():
    with pytest.raises(urltemplate.ExpansionError):
        urltemplate.expand("/x/{v}", [("v", "value")])


def test_expand_with_unsupported_value_type_raises():
    with pytest.raises(urltemplate.ExpansionError) as info:
        urltemplate.expand("/x/{v}", {"v": object()})
    assert "v" in str(info.value)


def test_expand_with_nan_value_raises():
    with pytest.raises(urltemplate.ExpansionError):
        urltemplate.expand("/x/{v}", {"v": float("nan")})


def test_expand_with_infinity_value_raises():
    with pytest.raises(urltemplate.ExpansionError):
        urltemplate.expand("/x/{v}", {"v": float("inf")})


def test_expand_with_none_inside_list_raises():
    with pytest.raises(urltemplate.ExpansionError):
        urltemplate.expand("/x/{v}", {"v": ["a", None]})


def test_expand_with_object_inside_list_raises():
    with pytest.raises(urltemplate.ExpansionError):
        urltemplate.expand("/x/{v}", {"v": ["a", object()]})


def test_uri_template_constructor_rejects_non_string():
    with pytest.raises(TypeError):
        urltemplate.URITemplate(42)


def test_template_syntax_error_position_attribute():
    error = urltemplate.TemplateSyntaxError("msg", position=5)
    assert error.position == 5


def test_template_syntax_error_position_default_none():
    error = urltemplate.TemplateSyntaxError("msg")
    assert error.position is None


def test_expand_top_level_with_no_variables_argument_works():
    assert urltemplate.expand("/static") == "/static"


def test_uri_template_expand_with_no_variables_argument_works():
    assert urltemplate.URITemplate("/static").expand() == "/static"

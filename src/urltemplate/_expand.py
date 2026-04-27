"""RFC 6570 expansion engine for parsed URI templates (levels 1-3)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ._encode import encode_reserved, encode_unreserved
from ._errors import ExpansionError
from ._parser import Component, Expression, Literal, VarSpec


@dataclass(frozen=True)
class _OperatorRules:
    prefix: str
    separator: str
    named: bool
    empty_value: str
    allow_reserved: bool


_RULES = {
    "":  _OperatorRules(prefix="",  separator=",", named=False, empty_value="", allow_reserved=False),
    "+": _OperatorRules(prefix="",  separator=",", named=False, empty_value="", allow_reserved=True),
    "#": _OperatorRules(prefix="#", separator=",", named=False, empty_value="", allow_reserved=True),
    ".": _OperatorRules(prefix=".", separator=".", named=False, empty_value="", allow_reserved=False),
    "/": _OperatorRules(prefix="/", separator="/", named=False, empty_value="", allow_reserved=False),
    ";": _OperatorRules(prefix=";", separator=";", named=True,  empty_value="", allow_reserved=False),
    "?": _OperatorRules(prefix="?", separator="&", named=True,  empty_value="=", allow_reserved=False),
    "&": _OperatorRules(prefix="&", separator="&", named=True,  empty_value="=", allow_reserved=False),
}


def expand(components, variables):
    if not isinstance(variables, Mapping):
        raise ExpansionError(f"variables must be a Mapping, got {type(variables).__name__}")
    pieces = []
    for component in components:
        if isinstance(component, Literal):
            pieces.append(component.text)
        elif isinstance(component, Expression):
            pieces.append(_expand_expression(component, variables))
        else:
            raise ExpansionError(f"unknown component type: {type(component).__name__}")
    return "".join(pieces)


def _expand_expression(expression, variables):
    rules = _RULES[expression.operator]
    rendered = []
    for var_spec in expression.variables:
        rendered_var = _expand_var(var_spec, variables, rules)
        if rendered_var is not None:
            rendered.append(rendered_var)
    if not rendered:
        return ""
    return rules.prefix + rules.separator.join(rendered)


def _expand_var(var_spec, variables, rules):
    raw_value = variables.get(var_spec.name)
    if raw_value is None:
        return None
    if isinstance(raw_value, str):
        return _render_string(var_spec.name, raw_value, rules)
    if isinstance(raw_value, bool):
        return _render_string(var_spec.name, "true" if raw_value else "false", rules)
    if isinstance(raw_value, (int, float)):
        return _render_string(var_spec.name, _format_number(raw_value), rules)
    if isinstance(raw_value, Mapping):
        if not raw_value:
            return None
        return _render_associative(var_spec.name, raw_value, rules)
    if isinstance(raw_value, Sequence) and not isinstance(raw_value, (str, bytes, bytearray)):
        if len(raw_value) == 0:
            return None
        return _render_list(var_spec.name, raw_value, rules)
    raise ExpansionError(f"variable {var_spec.name!r} has unsupported value type {type(raw_value).__name__}")


def _format_number(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ExpansionError("numeric value must be finite")
        if value.is_integer():
            return str(int(value))
        return repr(value)
    return str(value)


def _encode(value, rules):
    return encode_reserved(value) if rules.allow_reserved else encode_unreserved(value)


def _render_string(name, value, rules):
    encoded = _encode(value, rules)
    if not rules.named:
        return encoded
    if value == "":
        return name + rules.empty_value
    return f"{name}={encoded}"


def _render_list(name, items, rules):
    encoded_items = [_encode(_coerce_item(item, name), rules) for item in items]
    joined = ",".join(encoded_items)
    if not rules.named:
        return joined
    return f"{name}={joined}"


def _render_associative(name, mapping, rules):
    pairs = []
    for key, value in mapping.items():
        pairs.append(_encode(_coerce_item(key, name), rules))
        pairs.append(_encode(_coerce_item(value, name), rules))
    joined = ",".join(pairs)
    if not rules.named:
        return joined
    return f"{name}={joined}"


def _coerce_item(item, owner_name):
    if item is None:
        raise ExpansionError(f"{owner_name!r}: composite values may not contain None")
    if isinstance(item, bool):
        return "true" if item else "false"
    if isinstance(item, (int, float)):
        return _format_number(item)
    if isinstance(item, str):
        return item
    raise ExpansionError(f"{owner_name!r}: composite element of type {type(item).__name__} is not supported")

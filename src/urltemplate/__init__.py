"""urltemplate — RFC 6570 URI Template expansion (levels 1-3)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ._encode import encode_reserved, encode_unreserved
from ._errors import ExpansionError, TemplateSyntaxError, URITemplateError
from ._expand import expand as _expand_components
from ._parser import Component, Expression, Literal, VarSpec, parse

__all__ = [
    "expand",
    "parse",
    "URITemplate",
    "URITemplateError",
    "TemplateSyntaxError",
    "ExpansionError",
    "Literal",
    "Expression",
    "VarSpec",
    "Component",
    "encode_unreserved",
    "encode_reserved",
]

__version__ = "0.1.0"


def expand(template, variables=None):
    components = parse(template)
    return _expand_components(components, variables or {})


class URITemplate:
    __slots__ = ("_template", "_components")

    def __init__(self, template):
        if not isinstance(template, str):
            raise TypeError(f"template must be a string, got {type(template).__name__}")
        self._template = template
        self._components = parse(template)

    @property
    def template(self):
        return self._template

    @property
    def components(self):
        return self._components

    @property
    def variables(self):
        seen = {}
        for component in self._components:
            if isinstance(component, Expression):
                for var_spec in component.variables:
                    seen.setdefault(var_spec.name, None)
        return tuple(seen)

    def expand(self, variables=None):
        return _expand_components(self._components, variables or {})

    def __repr__(self):
        return f"URITemplate({self._template!r})"

    def __eq__(self, other):
        if not isinstance(other, URITemplate):
            return NotImplemented
        return self._template == other._template

    def __hash__(self):
        return hash(self._template)

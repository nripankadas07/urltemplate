"""Parser for RFC 6570 URI templates (levels 1-3)."""

from __future__ import annotations

from dataclasses import dataclass

from ._errors import TemplateSyntaxError

_OPERATORS = frozenset("+#./;?&")
_LEVEL_4_OPERATORS = frozenset("=,!@|")


@dataclass(frozen=True)
class VarSpec:
    name: str


@dataclass(frozen=True)
class Literal:
    text: str


@dataclass(frozen=True)
class Expression:
    operator: str
    variables: tuple


Component = Literal


def parse(template):
    if not isinstance(template, str):
        raise TypeError(f"template must be a string, got {type(template).__name__}")
    components = []
    buffer = []
    index = 0
    length = len(template)
    while index < length:
        char = template[index]
        if char == "{":
            if buffer:
                components.append(Literal("".join(buffer)))
                buffer.clear()
            expression, index = _parse_expression(template, index)
            components.append(expression)
            continue
        if char == "}":
            raise TemplateSyntaxError(f"unexpected '}}' at position {index}", index)
        _validate_literal_char(char, index)
        buffer.append(char)
        index += 1
    if buffer:
        components.append(Literal("".join(buffer)))
    return tuple(components)


def _validate_literal_char(char, position):
    if char in ("{", "}"):
        raise TemplateSyntaxError(f"brace character {char!r} appeared in literal context at {position}", position)
    code_point = ord(char)
    if code_point < 0x20 or code_point == 0x7F:
        raise TemplateSyntaxError(f"control character U+{code_point:04X} not allowed in literal at {position}", position)


def _parse_expression(template, start):
    end = template.find("}", start + 1)
    if end == -1:
        raise TemplateSyntaxError(f"unmatched '{{' starting at position {start}", start)
    body = template[start + 1 : end]
    if not body:
        raise TemplateSyntaxError(f"empty expression at position {start}", start)
    operator, body = _split_operator(body, start)
    if not body:
        raise TemplateSyntaxError(f"expression at position {start} has no variable list", start)
    variables = tuple(_parse_var_list(body, start))
    return Expression(operator=operator, variables=variables), end + 1


def _split_operator(body, expression_start):
    head = body[0]
    if head in _OPERATORS:
        return head, body[1:]
    if head in _LEVEL_4_OPERATORS:
        raise TemplateSyntaxError(f"operator {head!r} at position {expression_start + 1} is not part of levels 1-3", expression_start + 1)
    return "", body


def _parse_var_list(body, expression_start):
    raw_names = body.split(",")
    parsed = []
    cursor = expression_start + 1
    if body and body[0] in _OPERATORS:
        cursor += 1
    for raw_name in raw_names:
        if not raw_name:
            raise TemplateSyntaxError(f"empty variable name in expression starting at {expression_start}", expression_start)
        if "*" in raw_name:
            raise TemplateSyntaxError("explode modifier '*' is a level-4 feature; not supported", cursor + raw_name.index("*"))
        if ":" in raw_name:
            raise TemplateSyntaxError("prefix modifier ':' is a level-4 feature; not supported", cursor + raw_name.index(":"))
        _validate_var_name(raw_name, cursor)
        parsed.append(VarSpec(raw_name))
        cursor += len(raw_name) + 1
    return parsed


def _validate_var_name(name, position):
    if not name:
        raise TemplateSyntaxError("empty variable name", position)
    if name.startswith(".") or name.endswith("."):
        raise TemplateSyntaxError(f"variable name {name!r} may not start or end with '.'", position)
    if ".." in name:
        raise TemplateSyntaxError(f"variable name {name!r} contains consecutive dots", position)
    for offset, char in enumerate(name):
        if not (char.isalnum() or char in "_." or char == "%"):
            raise TemplateSyntaxError(f"invalid character {char!r} in variable name {name!r}", position + offset)

"""Exception classes for urltemplate."""

from __future__ import annotations


class URITemplateError(Exception):
    """Base class for all urltemplate errors."""


class TemplateSyntaxError(URITemplateError):
    """Raised when a template cannot be parsed.

    The optional ``position`` attribute gives the column (0-indexed) where
    the parser first detected a problem.
    """

    def __init__(self, message: str, position: int | None = None) -> None:
        super().__init__(message)
        self.position = position


class ExpansionError(URITemplateError):
    """Raised when a template parses but cannot be expanded against a
    supplied variable mapping (e.g., an unsupported value type)."""

"""Integration between the Bioregistry and Pydantic type annotations."""

from .api import (
    SemanticBody,
    SemanticField,
    SemanticForm,
    SemanticHeader,
    SemanticPath,
    SemanticQuery,
)
from .czzz import CURIE, Identifier, Prefix

__all__ = [
    "SemanticBody",
    "SemanticField",
    "SemanticForm",
    "SemanticHeader",
    "SemanticPath",
    "SemanticQuery",
    "CURIE",
    "Identifier",
    "Prefix",
]

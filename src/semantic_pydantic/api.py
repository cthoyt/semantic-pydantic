"""Integration between the Bioregistry and Pydantic type annotations.

Semantic Pydantic is a wrapper around :class:`pydantic.Field` and
FastAPI's :mod:`fastapi.param_functions` like :class:`fastapi.Path`
that enables annotating the semantic space from which data in that field
comes via the Bioregistry.
"""

from __future__ import annotations

from collections.abc import Callable
from textwrap import dedent
from typing import Any

import bioregistry
from pydantic import Field
from pydantic.fields import FieldInfo

__all__ = [
    "SemanticBody",
    "SemanticField",
    "SemanticForm",
    "SemanticHeader",
    "SemanticPath",
    "SemanticQuery",
]


def SemanticField(*args: Any, prefix: str, **kwargs: Any) -> FieldInfo:  # noqa:N802
    """Create a Pydantic Field, annotated with a Bioregistry prefix."""
    return _create(Field, *args, prefix=prefix, **kwargs)


def SemanticBody(*args: Any, prefix: str, **kwargs: Any) -> FieldInfo:  # noqa:N802
    """Create a FastAPI Body parameter, annotated with a Bioregistry prefix."""
    from fastapi import Body

    return _create(Body, *args, prefix=prefix, **kwargs)


def SemanticQuery(*args: Any, prefix: str, **kwargs: Any) -> FieldInfo:  # noqa:N802
    """Create a FastAPI Query parameter, annotated with a Bioregistry prefix."""
    from fastapi import Query

    return _create(Query, *args, prefix=prefix, **kwargs)


def SemanticPath(*args: Any, prefix: str, **kwargs: Any) -> FieldInfo:  # noqa:N802
    """Create a FastAPI Path parameter, annotated with a Bioregistry prefix."""
    from fastapi import Path

    return _create(Path, *args, prefix=prefix, **kwargs)


def SemanticHeader(*args: Any, prefix: str, **kwargs: Any) -> FieldInfo:  # noqa:N802
    """Create a FastAPI Header parameter, annotated with a Bioregistry prefix."""
    from fastapi import Header

    return _create(Header, *args, prefix=prefix, **kwargs)


def SemanticForm(*args: Any, prefix: str, **kwargs: Any) -> FieldInfo:  # noqa:N802
    """Create a FastAPI Form parameter, annotated with a Bioregistry prefix."""
    from fastapi import Form

    return _create(Form, *args, prefix=prefix, **kwargs)


def _create(
    func: Callable[..., FieldInfo],
    *args: Any,
    prefix: str,
    **kwargs: Any,
) -> FieldInfo:
    record = bioregistry.get_resource(prefix)
    if record is None:
        raise ValueError(
            dedent(
                f"""
        Prefix is not registered in the Bioregistry: {prefix}. Please take one of following steps:

        - Check the registry at https://bioregistry.io/registry for correct spelling
        - Submit a new prefix request at https://github.com/biopragmatics/bioregistry/issues
        """
            )
        )
    jse = kwargs.setdefault("json_schema_extra", {})
    jse["bioregistry"] = {
        "prefix": record.prefix,
        "mappings": record.mappings,
    }

    if "title" not in kwargs:
        kwargs["title"] = record.get_name()
    if "description" not in kwargs:
        kwargs["description"] = _get_description(record)

    if pattern := record.get_pattern():
        if "pattern" not in kwargs:
            kwargs["pattern"] = pattern

    if example := record.get_example():
        if "example" not in kwargs:
            jse["example"] = example

    return func(*args, **kwargs)


def _get_description(record: bioregistry.Resource) -> str:
    return f"""\
<p>\
This field corresponds to a local unique identifier from <i>{record.get_name()}</i></a>.
</p>\
<h4>Provenance</h4>\
<p>\
The semantics of this field are derived from the
<a href="https://bioregistry.io/{record.prefix}"><code>{record.prefix}</code></a> entry in
the <a href="https://bioregistry.io">Bioregistry</a>: a registry of semantic web and linked
open data compact URI (CURIE) prefixes and URI prefixes.
</p>\
<h4>Description of Semantic Space</h4>\
{record.get_description()}
""".strip()

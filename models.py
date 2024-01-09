from textwrap import dedent

import bioregistry
from bioregistry.constants import PYDANTIC_1

__all__ = [
    "SemanticField",
    "SemanticPath",
    "SemanticBody",
]


def _get_description(record: bioregistry.Resource) -> str:
    return dedent(
        f"""\
    <p>This field corresponds to a local unique identifier from <i>{record.get_name()}</i></a>.</p>

    <p>
        The semantics of this field are derived from the
        <a href="https://bioregistry.io/{record.prefix}"><code>{record.prefix}</code></a> entry in
        the <a href="https://bioregistry.io">Bioregistry</a>: a registry of semantic web and linked 
        open data compact URI (CURIE) prefixes and URI prefixes. A real example of a local unique identifier
        from this semantic space is {record.get_example()}.
    </p>

    <h4>Description of Semantic Space</h4>

    {record.get_description()}.
    """
    )


def _create(cls, *args, prefix: str, **kwargs):
    record = bioregistry.get_resource(prefix)
    if record is None:
        raise ValueError(f"Unregistered prefix: {prefix}")
    if "title" not in kwargs:
        kwargs["title"] = record.get_name()
    if "description" not in kwargs:
        kwargs["description"] = _get_description(record)
    if PYDANTIC_1:
        if "regex" not in kwargs:
            kwargs["regex"] = record.get_pattern()
    else:
        if "pattern" not in kwargs:
            kwargs["pattern"] = record.get_pattern()
    jse = kwargs.setdefault("json_schema_extra", {})
    jse["bioregistry"] = {
        "prefix": record.prefix,
        "mappings": record.mappings,
    }
    examples = record.get_examples()
    if examples:
        jse["examples"] = examples
    return cls(*args, **kwargs)


def SemanticField(*args, prefix: str, **kwargs):
    from pydantic import Field

    return _create(Field, *args, prefix=prefix, **kwargs)


def SemanticBody(*args, prefix: str, **kwargs):
    from fastapi import Body

    return _create(Body, *args, prefix=prefix, **kwargs)


def SemanticPath(*args, prefix: str, **kwargs):
    from fastapi import Path

    return _create(Path, *args, prefix=prefix, **kwargs)

import bioregistry

from textwrap import dedent

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
        open data compact URI (CURIE) prefixes and URI prefixes.
    </p>

    <h4>Description of Semantic Space</h4>

    {record.get_description()}
    """
    )


def _create(cls, *args, prefix: str, **kwargs):
    record = bioregistry.get_resource(prefix)
    if record is None:
        raise ValueError
    if "title" not in kwargs:
        kwargs["title"] = record.get_name()
    if "description" not in kwargs:
        kwargs["description"] = _get_description(record)
    if "regex" not in kwargs:
        kwargs["regex"] = record.get_pattern()
    jse = kwargs.setdefault("json_schema_extra", {})
    jse["bioregistry"] = {
        "prefix": record.prefix,
        "mappings": record.mappings,
    }
    example = record.get_example()
    if example:
        jse["examples"] = [example]
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

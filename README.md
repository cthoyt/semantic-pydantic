# Semantic PyDantic

Goals:

1. Annotate data models to make them more FAIR
2. Annotate APIs to make them more FAIR

Methods:

You can create a data model with Pydantic by writing a class that contains
various instances `pydantic.Field`, which each hold onto metadata about how to validate
the attribute of the data model. Often, these fields correspond to local unique identifiers
from a given semantic space. Since the Bioregistry provides a comprehensive catalog of
these semantic spaces that can each be referenced using a _prefix_, it would make sense
that we could define the semantics of how a Field should be used based on what's in the Bioregistry.

1. Automatically add context like a title, a description, and examples
2. Automatically add validation information such as a regular expression pattern

2. Create an API that looks up other identiiers based on the main one, ORCID
3. Annotate both the data model for a person and the API that consumes an ORCID and produces instances of the
   data model

# Case Study

As a demonstration, we will build a data model and API that serves information about scholars.

## First Steps with Pydantic

We'll use [Open Researcher and Contributor (ORCID)](https://orcid.org/) identifier as a primary key,
include the researcher's name, and start with a single cross-reference, e.g., to the author's [DBLP](https://dblp.org/)
identifier. We'll encode this data model using [Pydantic](https://docs.pydantic.dev/latest/) in the Python
programming language as follows:

```python
from pydantic import BaseModel, Field


class ScholarV1(BaseModel):
    """A model representing a researcher, who might have several IDs on different services."""

    orcid: str = Field(...)
    name: str = Field(...)
    dblp: str | None = Field(None)


print(ScholarV1.schema_json(indent=2))
```

If we dump this model to get a JSON schema, we get the following:

```json
{
  "title": "ScholarV1",
  "description": "A model representing a researcher, who might have several IDs on different services.",
  "type": "object",
  "properties": {
    "orcid": {
      "title": "Orcid",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "dblp": {
      "title": "Dblp",
      "type": "string"
    }
  },
  "required": [
    "orcid",
    "name"
  ]
}
```

There are several places for improvement here:

1. Correct capitalization of the titles (`ORCID` instead of `Orcid` and `DBLP` instead of `Dblp`)
2. Add useful descriptions of what each field is
3. Have regular expression patterns to validate input
4. Give an example

All of these are possible to annotate into Pydantic's `Field` object, but it requires lots of effort and takes lots of
space. Even worse, this might have to be partially duplicated if multiple models share the same fields. In the example
below, I annotated ORCID but will skip the others for brevity.

```python
from pydantic import BaseModel, Field


class ScholarV2(BaseModel):
    """A model representing a researcher, who might have several IDs on different services."""

    orcid: str = Field(
        ...,
        title="ORCID",
        description="A stable, public identifier for a researcher from https://orcid.com",
        pattern="^\d{4}-\d{4}-\d{4}-\d{3}(\d|X)$",
        example="0000-0003-4423-4370",
    )
    name: str = Field(...)
    dblp: str | None = Field(None)


print(ScholarV2.schema_json(indent=2))
```

Now, we can see the nice improvements propagate through to the JSON schema:

```json
{
  "title": "ScholarV2",
  "description": "A model representing a researcher, who might have several IDs on different services.",
  "type": "object",
  "properties": {
    "orcid": {
      "title": "ORCID",
      "description": "A stable, public identifier for a researcher from https://orcid.com",
      "pattern": "^\\d{4}-\\d{4}-\\d{4}-\\d{3}(\\d|X)$",
      "example": "0000-0003-4423-4370",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "dblp": {
      "title": "Dblp",
      "type": "string"
    }
  },
  "required": [
    "orcid",
    "name"
  ]
}
```

However, this was a lot of work. It would be nice if there were some database of all the semantic spaces
in the semantic web and natural sciences that contained the name, description, regular expression pattern,
and examples. Then, we could draw from this database to automatically populate our fields.

## Bioregistry Magic

The good news is that such a database exists - it's called the [Bioregistry](https://bioregistry.io). Each semantic
space (e.g., ORCID, DBLP) gets what's called a _prefix_ which is usually an acronym for the name of the resource
that serves as the primary key for the semantic space. These prefixes are also useful in making references to
entities in the semantic space more FAIR (findable, accessible, interoperable, reusable) using the [compact
URI (CURIE) syntax](https://cthoyt.com/2021/09/14/curies.html), though this isn't the goal of this demo.

I've mocked some Python code that bridges Pydantic and the Bioregistry in this
repository (https://github.com/cthoyt/semantic-pydantic/). I'm calling it **semantic Pydantic** because it
lets us annotate our data models with external metadata (and because it rhymes).

Here's the same model as before, but now using a `SemanticField` that extends Pydantic's `Field`. It has a special
keyword `prefix` that lets you give a Bioregistry prefix, then it is smart enough to fill out all the fields
on its own. I also took the liberty of adding several more semantic spaces that identify scholars like
[Web of Science (wos)](https://bioregistry.io/wos.researcher),
[Scopus](https://bioregistry.io/scopus), and even [GitHub](https://bioregistry.io/github).

```python
from pydantic import BaseModel, Field

from semantic_pydantic import SemanticField


class Scholar(BaseModel):
    """A model representing a researcher, who might have several IDs on different services."""

    orcid: str = SemanticField(..., prefix="orcid")
    name: str = Field(..., example="Charles Tapley Hoyt")

    wos: str | None = SemanticField(default=None, prefix="wos.researcher")
    dblp: str | None = SemanticField(default=None, prefix="dblp.author")
    github: str | None = SemanticField(default=None, prefix="github")
    scopus: str | None = SemanticField(default=None, prefix="scopus")
    semion: str | None = SemanticField(default=None, prefix="semion")
    publons: str | None = SemanticField(default=None, prefix="publons.researcher")
    authorea: str | None = SemanticField(default=None, prefix="authorea.author")
 ```

## Web Application

### How to Run

The demo can be run by cloning the repository, installing its requirements, and
running the self-contained `app.py`.

```shell
git clone https://github.com/cthoyt/pydantic-semantic
cd pydantic-semantic
python -m pip install -r requirements.txt
python app.py
```

# Post Mortem

## Similar Things

- I don't want to mess around with CURIEs or URIs here or any of the issues that come along with them, so this is
  complementary to LinkML. This is more lightweight
- This is for directly when you know data is attached to a certain vocabulary, and want a universal way
  of referencing it rather than having to worry about (extended) prefix maps

## Future Ideas

A key feature of the Bioregistry is that it provides a way to take a local unique identifier for an entity
in a given semantic space and make a URL that points to a web page describing the entity. For example,
if you have an ORCID identifier, you can make a URL for the ORCID page following the format
`https://orcid.org/<put ID here>`. It would be very cool to extend Semantic Pydantic to add some
properties that auto-generate URLs, like in the following:

```python
from pydantic import BaseModel, Field

from semantic_pydantic import SemanticField


class Scholar(BaseModel):
    orcid: str = SemanticField(..., prefix="orcid")
    name: str = Field(...)


charlie = Scholar(orcid="0000-0003-4423-4370", name="Charles Tapley Hoyt")
assert charlie.orcid_url == 'https://orcid.org/0000-0003-4423-4370'
```

# Funding

This work was funded by the Chan Zuckerberg Initiative (CZI) under award 2023-329850.

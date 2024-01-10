# pydantic-semantic

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

## How is this different from LinkML

- I don't want to mess around with CURIEs or URIs here or any of the issues that come along with them
- This is for directly when you know data is attached to a certain vocabulary, and want a universal way
  of referencing it rather than having to worry about (extended) prefix maps

# Case Study

As a demonstration, we will build a data model and API that serves information about scholars.
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

1. Model a person, who has many different identifiers in different databases

   ```python
   from pydantic import BaseModel, Field

   from fields import SemanticField
    
    
   class Scholar(BaseModel):
       """A model representing a researcher, who might have several IDs on different services."""
    
       orcid: str = SemanticField(..., prefix="orcid")
       name: str = Field(..., json_schema_extra={"examples": ["Charles Tapley Hoyt"]})
    
       wos: str | None = SemanticField(default=None, prefix="wos.researcher")
       dblp: str | None = SemanticField(default=None, prefix="dblp.author")
       github: str | None = SemanticField(default=None, prefix="github")
       scopus: str | None = SemanticField(default=None, prefix="scopus")
       semion: str | None = SemanticField(default=None, prefix="semion")
       publons: str | None = SemanticField(default=None, prefix="publons.researcher")
       authorea: str | None = SemanticField(default=None, prefix="authorea.author")
    ```

   This includes cross-references to the [Web of Science (wos)](https://bioregistry.io/wos.researcher),
   [DBLP](https://bioregistry.io/dblp.researcher), [Scopus](https://bioregistry.io/scopus), and other semantic spaces
   that describe scholars.

2. Create an API that looks up other identiiers based on the main one, ORCID
3. Annotate both the data model for a person and the API that consumes an ORCID and produces instances of the
   data model

## How to Run

The demo can be run by cloning the repository, installing its requirements, and
running the self-contained `app.py`.

```shell
git clone https://github.com/cthoyt/pydantic-semantic
cd pydantic-semantic
python -m pip install -r requirements.txt
python app.py
```

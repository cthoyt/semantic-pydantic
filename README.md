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

## Example

1. Model a person, who has many different identifiers in different databases
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

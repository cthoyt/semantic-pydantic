# Semantic Pydantic

> Annotate your data models in Pydantic and APIs in FastAPI with the Bioregistry to make them more FAIR

The demo can be run by cloning the repository, installing its requirements, and
running the self-contained `app.py`.

```shell
git clone https://github.com/cthoyt/semantic-pydantic
cd semantic-pydantic
python -m pip install -r requirements.txt
python app.py
```

## Getting Started

You can use one of the several extensions to Pydantic and FastAPI's `Field` classes.

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

Similarly, this can be used in FastAPI.

```python
from fastapi import FastAPI
from semantic_pydantic import SemanticPath

app = FastAPI(title="Semantic Pydantic Demo")
Scholar = ...  # defined before


@app.get("/api/orcid/{orcid}", response_model=Scholar)
def get_scholar_from_orcid(orcid: str = SemanticPath(prefix="orcid")):
    """Get xrefs for a researcher in Wikidata, given ORCID identifier."""
    ...  # full implementation in https://github.com/cthoyt/semantic-pydantic
    return Scholar(...)
```

Here's what the Swagger UI looks like, including all the annotations on both the data model and endpoint arguments.

![](api-1.png)

## Funding

This work was funded by the Chan Zuckerberg Initiative (CZI) under award 2023-329850.

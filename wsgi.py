from fastapi import FastAPI
from pydantic import BaseModel, Field

from models import SemanticField, SemanticPath


class Person(BaseModel):
    """A person."""

    orcid: str = SemanticField(..., prefix="orcid")
    wikidata: str | None = SemanticField(default=None, prefix="wikidata")
    github: str | None = SemanticField(default=None, prefix="github")
    scopus: str | None = SemanticField(default=None, prefix="scopus")
    name: str = Field(...)


app = FastAPI()


@app.get("/api/person/{orcid}", response_model=Person)
def get_orcid(orcid: str = SemanticPath(prefix="orcid")):
    """Get a person from their ORCID identifier."""
    return Person(orcid=orcid)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)

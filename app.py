import requests
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from models import SemanticField, SemanticPath


class Scholar(BaseModel):
    """A model representing a researcher, who might have several IDs on different services."""

    orcid: str = SemanticField(..., prefix="orcid")
    label: str = Field(..., json_schema_extra={"examples": ["Charles Tapley Hoyt"]})

    github: str | None = SemanticField(default=None, prefix="github")
    scopus: str | None = SemanticField(default=None, prefix="scopus")
    publons: str | None = SemanticField(default=None, prefix="publons.researcher")
    semion: str | None = SemanticField(default=None, prefix="semion")
    dblp: str | None = SemanticField(default=None, prefix="dblp.author")
    wos: str | None = SemanticField(default=None, prefix="wos.researcher")
    authorea: str | None = SemanticField(default=None, prefix="authorea.author")


app = FastAPI(title="Semantic Pydantic Demo")


@app.get("/api/orcid/{orcid}", response_model=Scholar)
def get_orcid(orcid: str = SemanticPath(prefix="orcid")):
    """Get xrefs for a researcher in Wikidata, given ORCID identifier."""
    res = requests.get(
        "https://query.wikidata.org/sparql",
        params={"query": SPARQL_FORMAT % orcid, "format": "json"},
    ).json()
    return Scholar.validate(
        {key: value["value"] for key, value in res["results"]["bindings"][0].items()}
    )


@app.get("/")
def redirect_to_docs():
    """Redirect to the docs page."""
    return RedirectResponse("/docs")


SPARQL_FORMAT = """\
SELECT * WHERE {
  VALUES ?orcid { "%s" }
  ?entity wdt:P496 ?orcid ;
          rdfs:label ?label .
  FILTER (lang(?label) = 'en')
  OPTIONAL { ?entity wdt:P2037 ?github . }
  OPTIONAL { ?entity wdt:P1153 ?scopus . }
  OPTIONAL { ?entity wdt:P3829 ?publons . }
  OPTIONAL { ?entity wdt:P7671 ?semion . }
  OPTIONAL { ?entity wdt:P2456 ?dblp . }
  OPTIONAL { ?entity wdt:P1053 ?wos . }
  OPTIONAL { ?entity wdt:P5039 ?authorea . }   
}
LIMIT 1
"""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)

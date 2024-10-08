"""A demo of Semantic Pydantic."""

from __future__ import annotations

import requests
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from semantic_pydantic import SemanticField, SemanticPath

# TODO create decorator that adds derived fields with URLs for each semantic field


class Scholar(BaseModel):
    """A model representing a researcher, who might have several IDs on different services."""

    orcid: str = SemanticField(..., prefix="orcid")
    name: str = Field(..., example="Charles Tapley Hoyt")

    wos: str | None = SemanticField(default=None, prefix="wos.researcher")
    # override the Bioregistry's example for GitHub
    github: str | None = SemanticField(default=None, prefix="github", example="cthoyt")
    scopus: str | None = SemanticField(default=None, prefix="scopus")
    semion: str | None = SemanticField(default=None, prefix="semion")
    publons: str | None = SemanticField(default=None, prefix="publons.researcher")
    authorea: str | None = SemanticField(default=None, prefix="authorea.author")


app = FastAPI(title="Semantic Pydantic Demo")


@app.get("/api/orcid/{orcid}", response_model=Scholar)
def get_scholar_from_orcid(orcid: str = SemanticPath(prefix="orcid")):
    """Get xrefs for a researcher in Wikidata, given ORCID identifier."""
    res = requests.get(
        "https://query.wikidata.org/sparql",
        params={"query": SPARQL_FORMAT % orcid, "format": "json"},
        timeout=3,
    ).json()
        {key: value["value"] for key, value in res["results"]["bindings"][0].items()}
    )


@app.get("/", include_in_schema=False)
def redirect_to_docs():
    """Redirect to the docs page."""
    return RedirectResponse("/docs")


SPARQL_FORMAT = """\
SELECT * WHERE {
  VALUES ?orcid { "%s" }
  ?entity wdt:P496 ?orcid ;
          rdfs:label ?name .
  FILTER (lang(?name) = 'en')
  OPTIONAL { ?entity wdt:P2037 ?github . }
  OPTIONAL { ?entity wdt:P1153 ?scopus . }
  OPTIONAL { ?entity wdt:P3829 ?publons . }
  OPTIONAL { ?entity wdt:P7671 ?semion . }
  OPTIONAL { ?entity wdt:P1053 ?wos . }
  OPTIONAL { ?entity wdt:P5039 ?authorea . }
}
LIMIT 1
"""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)

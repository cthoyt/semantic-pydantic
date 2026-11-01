"""Trivial version test."""

import unittest
from typing import Annotated

import fastapi
from pydantic import BaseModel, Field
from starlette.testclient import TestClient

from semantic_pydantic import CURIE, Identifier, Prefix, SemanticField, SemanticPath
from semantic_pydantic.version import get_version

CHARLIE_ORCID = "0000-0003-4423-4370"


class Scholar(BaseModel):
    """A model representing a researcher, who might have several IDs on different services."""

    orcid: Annotated[str, SemanticField(prefix="orcid")]
    name: str = Field(examples=["Charles Tapley Hoyt"])
    github: Annotated[str | None, SemanticField(prefix="github", examples=["cthoyt"])] = None


class PrefixContainingModel(BaseModel):
    """A model containing a prefix."""

    prefix: Prefix


class CURIEContainingModel(BaseModel):
    """A model containing a CURIE."""

    curie: CURIE


class IdentifierContainingModel(BaseModel):
    """A model for a person."""

    orcid: Identifier


class TestAPI(unittest.TestCase):
    """Trivially test a version."""

    def test_field(self) -> None:
        """Test fields."""
        person = Scholar(orcid=CHARLIE_ORCID, name="Charles Tapley Hoyt")
        self.assertIsNone(person.github)

        with self.assertRaises(ValueError):
            Scholar(orcid=CHARLIE_ORCID + "XXX", name="Charles Tapley Hoyt")

    def test_fastapi(self) -> None:
        """Test API usage."""
        app = fastapi.FastAPI()

        @app.get("/{orcid}", response_model=Scholar)
        def route(orcid: Annotated[str, SemanticPath(prefix="orcid")]) -> Scholar:
            """Return"""
            return Scholar(orcid=orcid, name="Test Name")

        client = TestClient(app)
        res = client.get(f"/{CHARLIE_ORCID}")
        obj = Scholar(**res.json())
        self.assertEqual(obj.orcid, CHARLIE_ORCID)

    def test_prefix(self) -> None:
        """Test a prefix field."""
        value = PrefixContainingModel(prefix="go")
        self.assertEqual("go", value.prefix)

        value = PrefixContainingModel(prefix="GO")
        self.assertEqual("go", value.prefix)

        with self.assertRaises(ValueError):
            PrefixContainingModel(prefix="nope")

    def test_curie(self) -> None:
        """Test a CURIE field."""
        value = CURIEContainingModel(curie="go:1234567")
        self.assertEqual("go:1234567", value.curie)

        value = CURIEContainingModel(curie="GO:1234567")
        self.assertEqual("go:1234567", value.curie)

        with self.assertRaises(ValueError):
            CURIEContainingModel(curie="go:1234")  # too short

        with self.assertRaises(ValueError):
            CURIEContainingModel(curie="nope:nope")

    def test_identifier(self) -> None:
        """Test an identifier field."""
        value = IdentifierContainingModel(orcid=CHARLIE_ORCID)
        self.assertEqual(CHARLIE_ORCID, value.orcid)

        with self.assertRaises(ValueError):
            IdentifierContainingModel(orcid=CHARLIE_ORCID + "X")

    def test_version_type(self) -> None:
        """Test the version is a string.

        This is only meant to be an example test.
        """
        version = get_version()
        self.assertIsInstance(version, str)

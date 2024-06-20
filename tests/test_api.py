"""Trivial version test."""

import typing
import unittest

import fastapi
from pydantic import BaseModel, Field
from semantic_pydantic import SemanticField, SemanticPath
from semantic_pydantic.version import get_version
from starlette.testclient import TestClient

CHARLIE_ORCID = "0000-0003-4423-4370"


class Scholar(BaseModel):
    """A model representing a researcher, who might have several IDs on different services."""

    orcid: str = SemanticField(..., prefix="orcid")
    name: str = Field(..., example="Charles Tapley Hoyt")
    github: typing.Optional[str] = SemanticField(default=None, prefix="github", example="cthoyt")


class TestAPI(unittest.TestCase):
    """Trivially test a version."""

    def test_field(self):
        """Test fields."""
        person = Scholar(orcid=CHARLIE_ORCID, name="Charles Tapley Hoyt")
        self.assertIsNone(person.github)

        with self.assertRaises(ValueError):
            Scholar(orcid=CHARLIE_ORCID + "XXX", name="Charles Tapley Hoyt")

    def test_fastapi(self):
        """Test API usage."""
        app = fastapi.FastAPI()

        @app.get("/{orcid}", response_model=Scholar)
        def route(orcid: str = SemanticPath(prefix="orcid")):
            """Return"""
            return Scholar(orcid=orcid, name="Test Name")

        client = TestClient(app)
        res = client.get(f"/{CHARLIE_ORCID}")
        obj = Scholar(**res.json())
        self.assertEqual(obj.orcid, CHARLIE_ORCID)

    def test_version_type(self):
        """Test the version is a string.

        This is only meant to be an example test.
        """
        version = get_version()
        self.assertIsInstance(version, str)

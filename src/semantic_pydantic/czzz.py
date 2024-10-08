"""Special forms."""

from __future__ import annotations

from typing import Any

import bioregistry
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import PydanticCustomError, core_schema

from semantic_pydantic.api import _get_description


class Prefix(str):
    """A Bioregistry prefix."""

    @classmethod
    def _validate(cls, __input_value: str, _: core_schema.ValidationInfo) -> Prefix:
        resource = bioregistry.get_resource(__input_value)
        if resource is None:
            raise PydanticCustomError("bioregistry_prefix", "Invalid Bioregistry prefix")
        return cls(resource.prefix)  # this automatically gets the standard part

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.AfterValidatorFunctionSchema:
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @property
    def name(self) -> str:
        """Get the name for this prefix."""
        _name = bioregistry.get_name(self)
        if _name is None:
            raise RuntimeError
        return _name

    @property
    def description(self) -> str:
        """Get the description for this prefix."""
        _description = bioregistry.get_description(self)
        if _description is None:
            raise RuntimeError
        return _description


class CURIE(str):
    """A Bioregistry CURIE."""

    @classmethod
    def _validate(cls, __input_value: str, _: core_schema.ValidationInfo) -> CURIE:
        prefix, _sep, identifier = __input_value.rpartition(":")
        resource = bioregistry.get_resource(prefix)
        if resource is None:
            raise PydanticCustomError(
                "bioregistry_curie", f"Invalid Bioregistry prefix ({prefix}) in {__input_value}"
            )
        if not resource.is_valid_identifier(identifier):
            raise PydanticCustomError(
                "bioregistry_curie",
                f"Invalid Bioregistry local unique identifier in "
                f"{__input_value}, does not match {resource.get_pattern()}",
            )
        return cls(bioregistry.curie_to_str(resource.prefix, identifier))

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.AfterValidatorFunctionSchema:
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )


class Identifier(str):
    """A factory for identifier annotations."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler) -> core_schema.CoreSchema:
        if not handler.field_name:
            raise RuntimeError
        resource = bioregistry.get_resource(handler.field_name)
        if resource is None:
            raise ValueError("can not apply to fields that aren't bioregistry normalizable")
        return core_schema.str_schema(
            pattern=resource.get_pattern(),
            metadata={"resource": resource},
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        resource: bioregistry.Resource = schema["metadata"]["resource"]
        json_schema = handler(schema)
        json_schema.update(
            {
                "title": resource.get_name(),
                "description": _get_description(resource),
            }
        )
        if example := resource.get_example():
            json_schema["example"] = example
        return json_schema

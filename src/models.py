from pydantic import BaseModel, Field, field_validator


SUPPORTED_PARAM_TYPES = {"number", "integer", "string"}


class ParamSpec(BaseModel):
    """Type information of a parameter or of a return value."""

    type: str


class FuncDef(BaseModel):
    """One function of the functions definition file."""

    name: str = Field(min_length=1)
    description: str
    parameters: dict[str, ParamSpec]
    returns: ParamSpec

    @field_validator("parameters")
    @classmethod
    def check_param_types(
        cls, value: dict[str, ParamSpec]
    ) -> dict[str, ParamSpec]:
        """Reject parameter types the generator cannot produce."""
        for name, spec in value.items():
            if spec.type not in SUPPORTED_PARAM_TYPES:
                raise ValueError(
                    f"unsupported type '{spec.type}' for parameter '{name}'"
                )
        return value


class PromptDef(BaseModel):
    """One function of the function calling file"""

    prompt: str = Field(min_length=1)



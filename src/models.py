from pydantic import BaseModel, Field
from typing import Literal


class ParamSpec(BaseModel):
    """Type information of a parameter or of a return value."""

    type: Literal["number", "string"]


class FuncDef(BaseModel):
    """One function of the functions definition file."""

    name: str = Field(min_length=1)
    description: str
    parameters: dict[str, ParamSpec]
    returns: ParamSpec


class PromptDef(BaseModel):
    """One function of the function calling file"""

    prompt: str = Field(min_length=1)

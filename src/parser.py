import json
from pydantic import BaseModel, ValidationError
from .cli import Arguments
from .models import FuncDef, PromptDef


class Parser(BaseModel):
    """Parser for input and function definition JSON files.

    Attributes:
        _input_file (Path): Path to the input JSON file.
        _function_file (Path): Path to the function definition JSON file.
    """
    params: Arguments

    def parse_input_file(self) -> list[PromptDef]:
        """Parses and validates the input JSON file.

        Returns:
            list[dict]: The content of the input JSON file as a list of
            dictionaries.
        """
        if not self.params.input_file.exists():
            raise FileNotFoundError("File not found:" +
                                    f"{self.params.input_file}")
        if not self.params.input_file.is_file():
            raise ValueError(f"The path: {self.params.input_file}" +
                             "is not a file")
        prompt = []
        try:
            with open(self.params.input_file, "r") as file:
                json_file = json.load(file)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as error:
            raise ValueError(error)
        for index, item in enumerate(json_file):
            try:
                prompt.append(PromptDef.model_validate(item))
            except ValidationError as e:
                raise ValueError(f"Wrong JSON in {self.params.input_file}, "
                                 + f"function#{index} : {e}")
        return prompt

    def parse_function_file(self) -> list[FuncDef]:
        """Parses and validates the function definition JSON file.

        Returns:
            list[FuncDef]: A list of validated function definition models.
        """
        if not self.params.functions_definition.exists():
            raise FileNotFoundError("File not found:" +
                                    f"{self.params.functions_definition}")
        if not self.params.functions_definition.is_file():
            raise ValueError(f"The path: {self.params.functions_definition}" +
                             "is not a file")
        try:
            with open(self.params.functions_definition, "r") as file:
                json_file = json.load(file)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as error:
            raise ValueError(error)
        if not isinstance(json_file, list):
            raise ValueError("Must contain a valid JSON Array")
        if len(json_file) <= 0:
            raise ValueError("Need at least one function definition")
        funcs: list[FuncDef] = []
        for index, item in enumerate(json_file):
            try:
                funcs.append(FuncDef.model_validate(item))
            except ValidationError as e:
                raise ValueError("Wrong JSON in" +
                                 f"{self.params.functions_definition}, "
                                 + f"function#{index} : {e}")
        return funcs

    def retrieve_info(self,
                      input_file: list[PromptDef]) -> list[str]:
        """Retrieves values for a specific key from a list of dictionaries.

        Args:
            input_file (list[dict]): The list of dictionaries to extract info
            from.
            key (str): The dictionary key to look up.

        Returns:
            list[str]: A list of values associated with the specified key.
        """
        return [element.prompt for element in input_file]

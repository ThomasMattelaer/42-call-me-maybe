import json
from .cli import Arguments
from .models import FuncDef, PromptDef


class Parser:
    """Parser for input and function definition JSON files.

    Attributes:
        _input_file (Path): Path to the input JSON file.
        _function_file (Path): Path to the function definition JSON file.
    """

    def __init__(self, params: Arguments):
        """Initializes the Parser with command-line arguments.

        Args:
            params (Arguments): The parsed command-line arguments containing
            file paths.
        """
        self._input_file = params.input_file
        self._function_file = params.functions_definition

    def parse_input_file(self) -> list[PromptDef]:
        """Parses and validates the input JSON file.

        Returns:
            list[dict]: The content of the input JSON file as a list of
            dictionaries.
        """
        if not self._input_file.exists():
            raise FileNotFoundError(f"File not found: {self._input_file}")
        if not self._input_file.is_file():
            raise ValueError(f"The path: {self._input_file} is not a file")
        prompt = []
        try:
            with open(self._input_file, "r") as file:
                json_file = json.load(file)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as error:
            raise ValueError(error)
        for index, item in enumerate(json_file):
            try:
                prompt.append(PromptDef.model_validate(item))
            except ValueError as e:
                raise ValueError(f"Wrong JSON in {self._input_file}, "
                                 + f"function#{index} : {e}")
        return prompt

    def parse_function_file(self) -> list[FuncDef]:
        """Parses and validates the function definition JSON file.

        Returns:
            list[FuncDef]: A list of validated function definition models.
        """
        if not self._function_file.exists():
            raise FileNotFoundError(f"File not found: {self._function_file}")
        if not self._function_file.is_file():
            raise ValueError(f"The path: {self._function_file} is not a file")
        try:
            with open(self._function_file, "r") as file:
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
            except ValueError as e:
                raise ValueError(f"Wrong JSON in {self._function_file}, "
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

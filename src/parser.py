import json
from .cli import Arguments


class Parser():
    def __init__(self, params: Arguments):
        self._input_file = params.input_file
        self._function_file = params.functions_definition

    def parse_input_file(self) -> list[dict]:
        if not self._input_file.exists():
            raise FileNotFoundError(f"File not found: {self._input_file}")
        if not self._input_file.is_file():
            raise ValueError(f"The path: {self._input_file} is not a file")
        try:
            with open(self._input_file, "r") as file:
                json_file = json.load(file)
            self.is_prompt_present(json_file)
            return json_file
        except json.JSONDecodeError as error:
            raise ValueError(error)

    def parse_function_file(self) -> list[dict]:
        if not self._input_file.exists():
            raise FileNotFoundError(f"File not found: {self._input_file}")
        if not self._input_file.is_file():
            raise ValueError(f"The path: {self._input_file} is not a file")
        try:
            with open(self._function_file, "r") as file:
                json_file = json.load(file)
            self.is_keys_valid(json_file)
            return json_file
        except json.JSONDecodeError as error:
            raise ValueError(error)

    def is_prompt_present(self, json_file: list[dict]) -> bool:
        for element in json_file:
            if "prompt" not in element:
                raise ValueError("Prompt key missing")
        return True

    def is_keys_valid(self, json_file: list[dict]) -> bool:
        expected_keys = ["name", "description", "parameters", "returns"]
        for element in json_file:
            elements = [key for key in element.keys()]
            if sorted(elements) != sorted(expected_keys):
                raise ValueError("A key is missing")
        return True

    def retrieve_info(self, input_file: list[dict], key: str) -> list[str]:
        return [element[key] for element in input_file]




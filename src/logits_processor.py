from .models import FuncDef
from pydantic import BaseModel, Field


class ConstraintBuilder(BaseModel):
    """Builder for applying structural and semantic generation constraints.

    Attributes:
        functions (list[FuncDef]): List of available function definitions.
        id_dict (dict[int, str]): Mapping from token IDs to their text
        representations.
    """

    functions: list[FuncDef] = Field(validation_alias="functions_definitions")
    id_dict: dict[int, str]

    def pick_token(self, logits: list[float], authorized_id: set[int]) -> int:
        """Selects the best token index from logits among authorized IDs
        , masking others.

        Args:
            logits (list[float]): List of logit scores for all vocabulary
            tokens.
            authorized_id (set[int]): Set of token IDs that are allowed to be
            picked.

        Returns:
            int: The token ID with the highest logit among the authorized ones.
        """
        masked = [float("-inf")] * len(logits)
        for token_id in authorized_id:
            masked[token_id] = logits[token_id]
        return masked.index(max(masked))

    def get_function(self, name: str) -> FuncDef:
        """Retrieves a specific function definition by its name.

        Args:
            name (str): The name of the function to retrieve.

        Returns:
            FuncDef: The matching function definition model.

        Raises:
            StopIteration: If no function with the given name is found.
        """
        return next(f for f in self.functions if f.name == name)

    def get_key(self, param_name: str, index: int) -> str:
        """Formats a JSON parameter key string based on its position index.

        Args:
            param_name (str): The name of the parameter.
            index (int): The index of the parameter in the sequence
            (0 for the first, etc.).

        Returns:
            str: The formatted JSON key fragment string.
        """
        if index == 0:
            return '", "parameters": {"' + param_name + '": '
        else:
            return ', "' + param_name + '": '

    def authorized_function_name(self, text_generated: str) -> set[int]:
        """Determines token IDs that can validly continue any allowed
        function name.

        Args:
            text_generated (str): The prefix text generated so far.

        Returns:
            set[int]: A set of authorized token IDs.
        """
        authorized_id = set()
        names = [prompt.name for prompt in self.functions]
        for token_id, text in self.id_dict.items():
            if not text:
                continue
            candidat = text_generated + text
            for name in names:
                if name.startswith(candidat):
                    authorized_id.add(token_id)
        return authorized_id

    def authorized_parameters(self,
                              text_generated: str,
                              param_type: str) -> set[int]:
        """Determines token IDs authorized for parameter generation
        based on the expected type.

        Args:
            text_generated (str): The parameter text generated so far.
            param_type (str): The expected type of the
            parameter (e.g., "number").

        Returns:
            set[int]: A set of authorized token IDs.
        """
        if param_type == "number":
            return self.authorized_numbers(text_generated, allow_dot=True)
        elif param_type == "integer":
            return self.authorized_numbers(text_generated, allow_dot=False)
        return self.authorized_strings()

    def authorized_strings(self) -> set[int]:
        """Returns all valid non-empty token IDs for standard
        string generation.

        Returns:
            set[int]: A set of token IDs corresponding to valid text
            characters/tokens.
        """
        authorized_id = set()
        for token_id, text in self.id_dict.items():
            if not text:
                continue
            authorized_id.add(token_id)
        return authorized_id

    def authorized_numbers(self, text_value: str, allow_dot: bool) -> set[int]:
        """Determines token IDs authorized for numeric value generation.

        Args:
            text_value (str): The numeric string generated so far.

        Returns:
            set[int]: A set of authorized token IDs.
        """
        authorized_id = set()
        for token_id, text in self.id_dict.items():
            candidat = text_value + text
            if not text:
                continue
            if ((text == "," or text == "}")
               and self.is_complete_number(text_value)):
                authorized_id.add(token_id)
            elif (self.is_number_prefix(candidat, allow_dot)):
                authorized_id.add(token_id)
        return authorized_id

    def is_number_prefix(self, candidat: str, allow_dot: bool) -> bool:
        """Validates if a candidate string forms a valid numeric prefix.

        Args:
            candidat (str): The candidate string to check.

        Returns:
            bool: True if the candidate string is a valid number prefix, False
            otherwise.
        """
        valid_char = all(char in '0123456789-' for char in candidat)
        if allow_dot:
            valid_char = all(char in '0123456789.-' for char in candidat)
        first_char = "-" not in candidat[1:]
        max_one_dot = candidat.count(".") <= 1
        not_a_dot = candidat.startswith(".")
        following = candidat.startswith("-.")
        return (valid_char and first_char and max_one_dot and not not_a_dot
                and not following)

    def is_complete_number(self, value: str) -> bool:
        """Checks if a string represents a structurally complete number.

        Args:
            value (str): The numeric string to evaluate.

        Returns:
            bool: True if the number is complete (not ending in a dot or minus)
            , False otherwise.
        """
        return (not value == "" and not
                (value.endswith(".") or value.endswith("-")))

    def function_names(self) -> list[FuncDef]:
        """Retrieves the list of available function definitions.

        Returns:
            list[FuncDef]: The list of function definitions.
        """
        return self.functions

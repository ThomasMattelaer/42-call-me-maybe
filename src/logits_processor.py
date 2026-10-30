class ConstraintBuilder():
    def __init__(self,
                 functions_definitions: list[dict],
                 id_dict: dict[int, str]) -> None:
        self.functions = functions_definitions
        self.id_dict = id_dict

    def pick_token(self, logits: list[float], authorized_id: set[int]) -> int:
        masked = [float("-inf")] * len(logits)
        for token_id in authorized_id:
            masked[token_id] = logits[token_id]
        return masked.index(max(masked))

    def get_function(self, name: str) -> dict:
        return next(f for f in self.functions if f["name"] == name)

    def get_key(self, param_name: str, index: int) -> str:
        if index == 0:
            return '", "parameters": {"' + param_name + '": '
        else:
            return ', "' + param_name + '": '

    def authorized_function_name(self, text_generated: str) -> set[int]:
        authorized_id = set()
        names = [prompt["name"] for prompt in self.functions]
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
                              param_type: str,) -> set[int]:
        if param_type == "number":
            return self.authorized_numbers(text_generated)
        return self.authorized_strings()

    def authorized_strings(self) -> set[int]:
        authorized_id = set()
        for token_id, text in self.id_dict.items():
            if not text:
                continue
            authorized_id.add(token_id)
        return authorized_id

    def authorized_numbers(self, text_value: str) -> set[int]:
        authorized_id = set()
        for token_id, text in self.id_dict.items():
            candidat = text_value + text
            if not text:
                continue
            if ((text == "," or text == "}")
               and self.is_complete_number(text_value)):
                authorized_id.add(token_id)
            elif (self.is_number_prefix(candidat)):
                authorized_id.add(token_id)
        return authorized_id

    def is_number_prefix(self, candidat: str) -> bool:
        valid_char = all(char in '0123456789.-' for char in candidat)
        first_char = "-" not in candidat[1:]
        max_one_dot = candidat.count(".") <= 1
        not_a_dot = candidat.startswith(".")
        following = candidat.startswith("-.")
        return (valid_char and first_char and max_one_dot and not not_a_dot
                and not following)

    def is_complete_number(self, value: str) -> bool:
        return (not value == "" and not
                (value.endswith(".") or value.endswith("-")))

    def function_names(self) -> list[dict]:
        return self.functions

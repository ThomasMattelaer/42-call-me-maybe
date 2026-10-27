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
            return ', "' + param_name + '":'

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
            return self.authorized_numbers()
        return self.authorized_numbers()

    def authorized_numbers(self) -> set[int]:
        authorized_id = set()
        for token_id, text in self.id_dict.items():
            if not text:
                continue

            if all(char in '0123456789.-,}' for char in text):
                authorized_id.add(token_id)
        return authorized_id






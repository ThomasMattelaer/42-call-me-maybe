class ConstraintBuilder():
    def __init__(self, functions_definitions: list[dict]) -> None:
        self.functions = functions_definitions

    def authorized_function_name(self,
                                 text_generated: str,
                                 id_dict: dict[int, str]) -> set[int]:
        authorized_id = set()
        names = [prompt["name"] for prompt in self.functions]
        for token_id, text in id_dict.items():
            if not text:
                continue
            candidat = text_generated + text
            for name in names:
                if name.startswith(candidat):
                    authorized_id.add(token_id)
        return authorized_id

    





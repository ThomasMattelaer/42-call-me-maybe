from __future__ import annotations
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
    from llm_sdk import Small_LLM_Model as llm
    from .logits_processor import ConstraintBuilder


class Generator():
    def __init__(self,
                 model: llm,
                 builder: ConstraintBuilder,
                 id_dict: dict[int, str],
                 end_ids: set) -> None:
        self.model = model
        self.builder = builder
        self.id_dict = id_dict
        self.functions = builder.function_names()
        self.end_ids = end_ids

    def generate_call(self, user_request: str) -> dict:
        functions_str = self.functions_to_str(self.functions)
        prompt = (
            "You are a function calling assistant.\n"
            f"Available functions:\n{functions_str}\n\n"
            "Choose the function that best answers the user request.\n"
            f"###User Request: {user_request}\n"
            "###Response:\n"
            '{"name": "'
        )
        token = self.model.encode(prompt)
        token_list = token[0].tolist()
        output_text = '{"name": "'
        text_generated = self.generate_name(token_list)
        text_value = self.generate_parmams(text_generated, token_list)
        output_text += text_generated
        function_obj = self.builder.get_function(text_generated)
        output_text += text_value
        output_text += "}}"
        final_json = json.loads(output_text)
        self.set_type(final_json, function_obj)
        return (final_json)

    def generate_name(self,
                      token_list: list[int]) -> str:
        text_generated = ""
        for _ in range(100):
            logits = self.model.get_logits_from_input_ids(token_list)
            next_token_id = self.builder.pick_token(
                logits,
                self.builder.authorized_function_name(text_generated)
            )
            if text_generated in [func["name"] for func in self.functions]:
                break
            token_list.append(next_token_id)
            text_generated += self.id_dict[next_token_id]
        return text_generated

    def generate_parmams(self,
                         text_generated: str,
                         token_list: list[int]) -> str:
        function_obj = self.builder.get_function(text_generated)
        parameters = enumerate(function_obj["parameters"].items())
        text = ""
        for index, (param_name, param_info) in parameters:
            text_value = ""
            params_type = param_info["type"]
            params_encode = self.model.encode(
                self.builder.get_key(param_name, index)
            )
            params_token = params_encode[0].tolist()
            token_list += params_token
            text += self.model.decode(params_token)
            for i in range(100):
                logits = self.model.get_logits_from_input_ids(token_list)
                next_token_id = self.builder.pick_token(
                    logits,
                    self.builder.authorized_parameters(text_value, params_type)
                )
                if next_token_id in self.end_ids:
                    break
                token_list.append(next_token_id)
                text_value += self.id_dict[next_token_id]
            text += text_value
        return text

    def functions_to_str(self, input_file: list[dict]) -> str:
        return json.dumps(input_file)

    def set_type(self, json_file: dict, func_obj: dict) -> None:
        for (name, info) in func_obj["parameters"].items():
            param_type = info["type"]
            value = json_file["parameters"][name]
            if param_type == "number":
                json_file["parameters"][name] = float(value)

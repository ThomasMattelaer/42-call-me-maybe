from __future__ import annotations
from typing import TYPE_CHECKING, Any
from .prompts import build_prompt
from .models import FuncDef
from pydantic import BaseModel, Field
import json

if TYPE_CHECKING:
    from .logits_processor import ConstraintBuilder


class Generator(BaseModel):
    """Handles text generation constrained by structured function definitions
    and token masks.

    Attributes:
        model (llm): The underlying small language model used for token
        generation.
        builder (ConstraintBuilder): The helper responsible for building
        constraints and picking tokens.
        id_dict (dict[int, str]): Mapping from token IDs to their
        corresponding text strings.
        functions (list[FuncDef]): List of available function definitions.
        end_ids (dict[str, set[int]]): Mapping of parameter types to their
        termination token IDs.
    """
    model_config = {"arbitrary_types_allowed": True}

    model: Any
    builder: ConstraintBuilder
    id_dict: dict[int, str]
    end_ids: dict[str, set[int]]

    def generate_call(self, user_request: str) -> dict:
        """Generates a structured function call JSON dictionary based on the
        user request.

        Args:
            user_request (str): The natural language request from the user.

        Returns:
            dict: The parsed and type-corrected JSON representing the
            function call.
        """
        functions_str = self.functions_to_str(self.builder.functions)
        print(user_request)
        prompt = build_prompt(functions_str, user_request)
        token = self.model.encode(prompt)
        token_list = token[0].tolist()
        output_text = '{"prompt": ' + json.dumps(user_request) + ', "name": "'
        text_generated = self.generate_name(token_list)
        text_value = self.generate_parmams(text_generated, token_list)
        output_text += text_generated
        function_obj = self.builder.get_function(text_generated)
        output_text += text_value
        output_text += "}}"
        print(output_text)
        final_json: dict = json.loads(output_text)
        self.set_type(final_json, function_obj)
        return (final_json)

    def generate_name(self,
                      token_list: list[int]) -> str:
        """Generates the function name token-by-token under strict naming
        constraints.

        Args:
            token_list (list[int]): The current list of context token IDs.

        Returns:
            str: The generated function name string.
        """
        text_generated = ""
        for _ in range(100):
            logits = self.model.get_logits_from_input_ids(token_list)
            next_token_id = self.builder.pick_token(
                logits,
                self.builder.authorized_function_name(text_generated)
            )
            if text_generated in [f.name for f in self.builder.functions]:
                break
            token_list.append(next_token_id)
            text_generated += self.id_dict[next_token_id]
        return text_generated

    def generate_parmams(self,
                         text_generated: str,
                         token_list: list[int]) -> str:
        """Generates parameter values for the selected function token-by-token.

        Args:
            text_generated (str): The function name generated so far.
            token_list (list[int]): The current list of context token IDs.

        Returns:
            str: The formatted JSON text snippet containing the generated
            parameters.
        """
        function_obj = self.builder.get_function(text_generated)
        parameters = enumerate(function_obj.parameters.items())
        text = ""
        for index, (param_name, param_info) in parameters:
            text_value = ""
            params_type = param_info.type
            key_text = self.builder.get_key(param_name, index)
            if params_type == "string":
                token_text = key_text + '"'
            else:
                token_text = key_text
            params_encode = self.model.encode(token_text)
            params_token = params_encode[0].tolist()
            token_list += params_token
            text += key_text
            for i in range(100):
                logits = self.model.get_logits_from_input_ids(token_list)
                next_token_id = self.builder.pick_token(
                    logits,
                    self.builder.authorized_parameters(text_value, params_type)
                )
                if '"' in self.id_dict[next_token_id]:
                    text_value += self.id_dict[next_token_id].split('"')[0]
                    break
                if next_token_id in self.end_ids[params_type]:
                    break
                token_list.append(next_token_id)
                text_value += self.id_dict[next_token_id]
            if params_type == "string":
                text += json.dumps(text_value)
            else:
                text += text_value

        return text

    def functions_to_str(self, functions: list[FuncDef]) -> str:
        """Describe the available functions as compact signatures.

        Args:
            functions: The validated function definitions.

        Returns:
            One line per function: name(param: type, ...) - description.
        """
        lines = []
        for func in functions:
            params = ", ".join(
                f"{name}: {spec.type}"
                for name, spec in func.parameters.items()
            )
            lines.append(f"{func.name}({params}) - {func.description}")
        return "\n".join(lines)

    def set_type(self, json_file: dict, func_obj: FuncDef) -> None:
        """Casts generated parameter values in the JSON dictionary to their
        correct target types.

        Args:
            json_file (dict): The parsed function call dictionary to modify in
            place.
            func_obj (FuncDef): The function definition model containing
            expected parameter types.
        """
        for (name, info) in func_obj.parameters.items():
            param_type = info.type
            value = json_file["parameters"][name]
            if param_type == "number":
                json_file["parameters"][name] = float(value)

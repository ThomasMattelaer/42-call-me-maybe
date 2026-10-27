from .cli import parse_arguments
from .parser import Parser
from llm_sdk import Small_LLM_Model as llm
from .logits_processor import ConstraintBuilder
import json

if __name__ == "__main__":
    print("Working")
    try:
        params = parse_arguments()
        parser = Parser(params)
        input_file = parser.parse_input_file()
        function_file = parser.parse_function_file()
        prompts = parser.retrieve_info(input_file, "prompt")
        functions_str = parser.functions_to_str(function_file)
        user_request = "What is the sum of 2 and 3?"
        model = llm()
        prompt = (
            "You are a function calling assistant.\n"
            f"Available functions:\n{functions_str}\n\n"
            "Choose the function that best answers the user request.\n"
            f"###User Request: {user_request}\n"
            "###Response:\n"
            '{"name": "'
        )

        token = model.encode(prompt)
        token_list = token[0].tolist()
        prompt_len = len(token_list)
        vocab = model.get_path_to_vocab_file()
        with open(vocab, 'r') as file:
            token_dict = json.load(file)
        comma_id = token_dict[","]
        brace_id = token_dict["}"]
        end_ids = {comma_id, brace_id}
        id_dict = {val: key for key, val in token_dict.items()}
        builder = ConstraintBuilder(function_file, id_dict)
        text_generated = ""
        for _ in range(50):
            if text_generated in [func["name"] for func in function_file]:
                break
            logits = model.get_logits_from_input_ids(token_list)
            next_token_id = builder.pick_token(
                logits,
                builder.authorized_function_name(text_generated)
            )
            token_list.append(next_token_id)
            text_generated += id_dict[next_token_id]
            print(f"Next token ID: {next_token_id}: '{id_dict[next_token_id]}'")
        print(text_generated)
        ## Generation of the parameters:
        function_obj = builder.get_function(text_generated)
        parameters = enumerate(function_obj["parameters"].items())
        for index, (param_name, param_info) in parameters:
            text_value = ""
            params_type = param_info["type"]
            params_encode = model.encode(builder.get_key(param_name, index))
            params_token = params_encode[0].tolist()
            token_list += params_token
            for i in range(20):
                if next_token_id in end_ids:
                    print("over")
                    break
                logits = model.get_logits_from_input_ids(token_list)
                next_token_id = builder.pick_token(
                    logits,
                    builder.authorized_parameters(text_value, params_type)
                )
                token_list.append(next_token_id)
                text_value += id_dict[next_token_id]
                print(f"Next token ID: {next_token_id}: '{id_dict[next_token_id]}'")
            print(text_value)
        print(model.decode(token_list[prompt_len:]))
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")

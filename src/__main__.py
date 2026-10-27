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
        user_request = "Greet Shrek"
        model = llm()
        prompt = (
            "You are a function calling assistant.\n"
            f"Available functions:\n{functions_str}\n\n"
            "Choose the function that best answers the user request.\n"
            f"###User Request: {user_request}\n"
            "###Response:\n"
            '{"name": "'
        )
        builder = ConstraintBuilder(function_file)
        token = model.encode(prompt)
        token_list = token[0].tolist()
        prompt_len = len(token_list)
        vocab = model.get_path_to_vocab_file()
        with open(vocab, 'r') as file:
            token_dict = json.load(file)
        id_dict = {val: key for key, val in token_dict.items()}
        text_generated = ""
        for _ in range(50):
            if text_generated in [func["name"] for func in function_file]:
                break
            logits = model.get_logits_from_input_ids(token_list)
            authorized_id = builder.authorized_function_name(text_generated, id_dict)
            masked = [float("-inf")] * len(logits)
            for token_id in authorized_id:
                masked[token_id] = logits[token_id]
            next_token_id = masked.index(max(masked))
            token_list.append(next_token_id)
            text_generated += id_dict[next_token_id]
            print(f"Next token ID: {next_token_id}: '{id_dict[next_token_id]}'")
        print(text_generated)
        function = next(func for func in function_file if func["name"] == text_generated)
        func_params: dict = function["parameters"]
        print(list(func_params.keys()))
        params_text = '", "parameters": {"' + list(func_params)[0] + '": '
        params_encode = model.encode(params_text)
        params_token = params_encode[0].tolist()
        token_list += params_token
        print(model.decode(token_list[prompt_len:]))
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")

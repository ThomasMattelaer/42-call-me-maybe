from .cli import parse_arguments
from .parser import Parser
from llm_sdk import Small_LLM_Model as llm

if __name__ == "__main__":
    print("Working")
    try:
        params = parse_arguments()
        parser = Parser(params)
        input_file = parser.parse_input_file()
        function_file = parser.parse_function_file()
        prompts = parser.retrieve_info(input_file, "prompt")
        functions_str = parser.functions_to_str(function_file)
        for user_request in prompts:
            model = llm()
            prompt = f"""You are an intelligent assistant. You have access to
            the following tools/functions:
            {functions_str}
            Based on the user request below, determine which function to cal
            User Request: {user_request}
            Output the result in a strict JSON format with keys
            "promtp" "name" and "parameters".
            Example:
            {{"prompt": ""What is the sum of 2 and 3?"
            "name": "fn_add_numbers", "parameters": {{"a": 2.0, "b": 3.0}}}}
            Response:
            """
            token = model.encode(prompt)
            token_list = token[0].tolist()
            prompt_len = len(token_list)
            eos_id = model._tokenizer.eos_token_id
            next_token_id = None
            for _ in range(30):
                logits = model.get_logits_from_input_ids(token_list)
                next_token_id = logits.index(max(logits))
                token_list.append(next_token_id)
            response_token = token_list[prompt_len:]
            decode = model.decode(response_token)
            print(f"decode: {decode}")
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")

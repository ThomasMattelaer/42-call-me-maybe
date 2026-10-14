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
        # for user_request in prompts:
        user_request = "Greet Shrek"
        model = llm()
        prompt = f"""You are an intelligent assistant. You have access to
        the following tools/functions:
        {functions_str}
        Based on the user request below, determine which function to call
        ###User Request: {user_request}
        Output the result in a strict JSON format with keys
        "name" and "parameters" and stop it after providing this.
        Example:
        {{"name": "fn_add_numbers", "parameters": {{"a": 2.0, "b": 3.0}}}}
        ###Response:
        """
        token = model.encode(prompt)
        token_list = token[0].tolist()
        prompt_len = len(token_list)
        eos_id = model._tokenizer.eos_token_id
        print(f"last token_id : {eos_id}")
        next_token_id = None
        for _ in range(35):
            logits = model.get_logits_from_input_ids(token_list)
            next_token_id = logits.index(max(logits))
            print(next_token_id)
            if next_token_id == eos_id:
                break
            token_list.append(next_token_id)
        response_token = token_list[prompt_len:]
        decode = model.decode(response_token)
        print(f"decode: {decode}")
        try:
            json_response = parser.str_to_json(response_token)
            print(json_response)
            name = json_response.get("name", "")
            params = json_response.get("parameters")
        except ValueError:
            raise ValueError("issue with the output json")
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")

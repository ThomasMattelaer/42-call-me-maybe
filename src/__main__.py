from .cli import parse_arguments
from .parser import Parser
from llm_sdk import Small_LLM_Model as llm
from .logits_processor import ConstraintBuilder
from .generator import Generator
import json

if __name__ == "__main__":
    print("Working")
    try:
        params = parse_arguments()
        parser = Parser(params)
        input_file = parser.parse_input_file()
        prompts = parser.retrieve_info(input_file, "prompt")
        function_file = parser.parse_function_file()
        user_request = "What is the sum of 2 and 3?"
        model = llm()
        vocab = model.get_path_to_vocab_file()
        with open(vocab, 'r') as file:
            token_dict = json.load(file)
        comma_id = token_dict[","]
        brace_id = token_dict["}"]
        end_ids = {comma_id, brace_id}
        id_dict = {val: key for key, val in token_dict.items()}
        builder = ConstraintBuilder(function_file, id_dict)
        generator = Generator(model, builder, id_dict, end_ids)
        final_json = generator.generate_call(user_request)
        print(final_json)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")

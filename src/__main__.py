from .cli import parse_arguments
from .parser import Parser
from llm_sdk import Small_LLM_Model as llm
from .logits_processor import ConstraintBuilder
from .generator import Generator
import json
from pathlib import Path
import sys

if __name__ == "__main__":
    print("Working")
    try:
        params = parse_arguments()
        parser = Parser(params)
        input_file = parser.parse_input_file()
        prompts = parser.retrieve_info(input_file, "prompt")
        function_file = parser.parse_function_file()
        final_json: list[dict] = []
        model = llm()
        vocab = model.get_path_to_vocab_file()
        with open(vocab, 'r') as file:
            token_dict = json.load(file)
        comma_id = token_dict[","]
        brace_id = token_dict["}"]
        quote_id = token_dict['"']
        end_ids = {"number": {comma_id, brace_id}, "string": {quote_id}}
        id_dict_raw = {val: key for key, val in token_dict.items()}
        id_dict = {key: val.replace('Ġ', ' ').replace('Ċ', '\n')
                   for key, val in id_dict_raw.items()}
        builder = ConstraintBuilder(function_file, id_dict)
        generator = Generator(model, builder, id_dict, end_ids)
        for user_request in prompts:
            try:
                final_json.append(
                    generator.generate_call(json.dumps(user_request))
                )
            except json.JSONDecodeError as e:
                print(f" Error in Prompt: '{user_request}' : {e}",
                      file=sys.stderr)
        try:
            params.output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(params.output_file, "w") as f:
                json.dump(final_json, f, indent=2)
        except OSError as e:
            raise OSError(e)
    except (FileNotFoundError, ValueError, KeyError, OSError) as error:
        print(f"Error: {error}")

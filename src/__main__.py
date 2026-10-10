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
        definitions = parser.retrieve_info(function_file, "description")
        modle = llm()
        test = modle.encode("Given these function descriptions, which function should handle the request 'What is the sum of 2 and 3?'")
        print(f"test: {test}")
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")

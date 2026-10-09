from .cli import parse_arguments
from .parser import Parser

if __name__ == "__main__":
    print("Working")
    try:
        params = parse_arguments()
        parser = Parser(params)
        parser.parse_input_file()
        parser.parse_function_file()
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")

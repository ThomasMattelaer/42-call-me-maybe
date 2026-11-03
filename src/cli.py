from argparse import ArgumentParser
from pathlib import Path
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class Arguments(BaseModel):
    """Holds command-line configuration paths for input files and output
    results.

    Attributes:
        functions_definition (Path): Path to the JSON file defining available
        functions.
        input_file (Path): Path to the JSON test file containing user requests.
        output_file (Path): Path where the generated function calls JSON will
        be saved.
    """
    functions_definition: Path
    input_file: Path
    output_file: Path


def parse_arguments() -> Arguments:
    """Parses command-line arguments and returns them as a structured
    Arguments instance.

    Returns:
        Arguments: A dataclass instance containing the resolved file paths.
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--functions_definition",
        default=Path("data/input/functions_definition.json"),
        type=Path
    )
    parser.add_argument(
        "--input",
        default=Path("data/input/function_calling_tests.json"),
        type=Path
    )
    parser.add_argument(
        "--output",
        default=Path("data/output/function_calls.json"),
        type=Path)
    args = parser.parse_args()
    return Arguments(
        functions_definition=args.functions_definition,
        input_file=args.input,
        output_file=args.output
    )

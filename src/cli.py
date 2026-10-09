from argparse import ArgumentParser
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Arguments:
    functions_definition: Path
    input_file: Path
    output_file: Path


def parse_arguments() -> Arguments:
    parser = ArgumentParser()
    parser.add_argument("--functions_definition", required=True, type=Path)
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

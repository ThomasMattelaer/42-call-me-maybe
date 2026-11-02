import json
from typing import Any

EXAMPLES: list[tuple[str, dict[str, Any]]] = [
    ("Say hello to Brian",
     {"name": "fn_say_hello", "parameters": {"person": "Brian"}}),
    ("Replace spaces in 'a b c' with underscores",
     {"name": "fn_replace", "parameters":
      {"text": "a b c", "regex": " ", "replacement": "_"}}),
    ("Replace every capital letter in 'HeLLo' with dashes",
     {"name": "fn_replace", "parameters":
      {"text": "HeLLo", "regex": "[A-Z]", "replacement": "-"}}),
    ("Multiply 12 by 7",
     {"name": "fn_multiply", "parameters": {"a": 12.0, "b": 7.0}}),
    ("Replace every comma in 'a,b,c' with semicolons",
        {"name": "fn_replace", "parameters":
         {"text": "a,b,c", "regex": ",", "replacement": ";"}}),
]


def build_prompt(functions_str: str, user_request: str) -> str:
    """Build the few-shot prompt sent to the model."""
    shots = "\n\n".join(
        f"prompt: {request}\nanswer: {json.dumps(answer)}"
        for request, answer in EXAMPLES
    )
    return (
        "Choose the function that matches the prompt and extract its "
        "arguments.\n"
        "Copy values from the prompt. When a symbol is named "
        "Values never start or end with a space, unless the request ask for it"
        "(asterisks, dashes, underscores...), write the symbol itself. "
        "A regex is a pattern to search for, not the literal text.\n\n"
        f"Available functions:\n{functions_str}\n\n"
        "Unrelated examples of the answer format:\n\n"
        f"{shots}\n\n"
        f"prompt: {user_request}\n"
        'answer: {"name": "'
    )

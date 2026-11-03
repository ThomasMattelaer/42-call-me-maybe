import json
from typing import Any

EXAMPLES: list[tuple[str, dict[str, Any]]] = [
    ("Say hello to Brian",
     {"name": "fn_say_hello", "parameters": {"person": "Brian"}}),
    ("Replace every capital letter in 'HeLLo' with dashes",
     {"name": "fn_replace", "parameters":
      {"text": "HeLLo", "regex": "[A-Z]", "replacement": "-"}}),
    ("Multiply 12 by 7",
     {"name": "fn_multiply", "parameters": {"a": 12.0, "b": 7.0}}),
]


def build_prompt(functions_str: str, user_request: str) -> str:
    """Build the few-shot prompt sent to the model.

    Args:
        functions_str: The compact description of the functions.
        user_request: The natural language request, unescaped.

    Returns:
        The prompt, ending right before the function name.
    """
    shots = "\n".join(
        f"prompt: {request}\nanswer: {json.dumps(answer)}"
        for request, answer in EXAMPLES
    )
    return (
        "Pick the function matching the prompt and extract its "
        "arguments. Copy values from the prompt. A regex is a pattern, "
        "not the literal text. Write named symbols as the symbol itself. "
        "Values never start or end with a space unless requested.\n\n"
        f"Functions:\n{functions_str}\n\n"
        f"Examples:\n{shots}\n\n"
        f"prompt: {user_request}\n"
        'answer: {"name": "'
    )

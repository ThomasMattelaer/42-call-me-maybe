*This project has been created as part of the 42 curriculum by tmattela[, <login2>[, <login3>]].*

# call me maybe

Introduction to function calling in LLMs, using constrained decoding on a
small model (Qwen/Qwen3-0.6B).

## Description

Given a natural language request such as `"What is the sum of 40 and 2?"`,
the program does **not** answer the question. It returns the function call
that would solve it:

```json
{"prompt": "What is the sum of 40 and 2?",
 "name": "fn_add_numbers",
 "parameters": {"a": 40.0, "b": 2.0}}
```

A 0.6B parameter model is unreliable at producing JSON when it is only
prompted to. This project guarantees valid, schema-compliant output by
using **constrained decoding**: at every generation step, the logits of
tokens that would break the structure or the schema are set to `-inf`
before the next token is chosen.

The function name and the argument values are chosen by the LLM. The
program only decides which tokens the model is allowed to pick.

## Instructions

Requirements: Python 3.10+, [uv](https://github.com/astral-sh/uv).

```bash
make install   # uv sync
make run       # run with the default paths
make debug     # run under pdb
make lint      # flake8 + mypy
make clean     # remove caches
```

Command line:

```bash
uv run python -m src \
    --functions_definition data/input/functions_definition.json \
    --input data/input/function_calling_tests.json \
    --output data/output/function_calls.json
```

By default, inputs are read from `data/input/` and the result is written to
`data/output/function_calls.json` (the folder is created if needed).

## Example usage

Input (`function_calling_tests.json`):

```json
[{"prompt": "What is the sum of 2 and 3?"},
 {"prompt": "Greet shrek"}]
```

Output (`function_calls.json`):

```json
[
  {"prompt": "What is the sum of 2 and 3?",
   "name": "fn_add_numbers",
   "parameters": {"a": 2.0, "b": 3.0}},
  {"prompt": "Greet shrek",
   "name": "fn_greet",
   "parameters": {"name": "shrek"}}
]
```

## Algorithm explanation

Generation is token by token. The structure of the output is written by the
program, and the model only fills the gaps (the function name and each
argument value).

For one prompt:

1. The prompt (available functions, few-shot examples, the request) is
   encoded, followed by the start of the JSON: `{"name": "`.
2. **Function name.** At each step, the allowed tokens are those for which
   `generated_text + token_text` is still a prefix of at least one function
   name. All other logits are set to `-inf`, then the best remaining token
   is taken. The loop stops when the generated text is exactly a function
   name. Since the model scores the allowed tokens using the request, it is
   the model that chooses the function.
3. **Parameters.** The program looks up the chosen function in the
   definitions and writes the skeleton itself (`", "parameters": {"a": `).
   For each parameter, the model generates only the value, under a mask
   that depends on the parameter type taken from the definitions.
   - `number`: only digits, `.` and `-` are allowed, with a single `-` at
     the start and at most one `.`. The tokens `,` and `}` are allowed only
     when the value is already a complete number, and they act as the end
     of the value.
   - `string`: any token is allowed. A token containing a double quote ends
     the value, and only the text before the quote is kept.
4. The program closes the object, builds a Python dict (strings are kept as
   they are, `number` values are converted with `float`) and adds the
   original prompt.

The mapping between tokens and text comes from the vocabulary JSON file
(`get_path_to_vocab_file`). It is read once into a `token -> id` dict and
inverted into an `id -> text` dict, where the tokenizer symbols for spaces
and new lines are converted to real characters.

## Design decisions

- **The program writes the structure, the model fills the values.** Keys,
  separators and braces are never left to the model, so the JSON cannot be
  malformed.
- **Generation is separated from constraints.** `ConstraintBuilder` only
  knows the function definitions and the vocabulary and returns the allowed
  token ids. `Generator` owns the loop and the model.
- **The tokenizer vocabulary is loaded once.** The model, the vocabulary
  and the builder are created before the loop over the prompts. Reloading
  them for each prompt made the program very slow.
- **A quote inside a string value ends the value.** This is simpler and
  more robust than tracking escape sequences.
- **Strings are never pasted into JSON by hand.** Values are stored in a
  dict and escaped once by `json.dump`.
- **Few-shot examples in the prompt** use made-up function names that do
  not appear in the input files, and show a pattern as a regex and symbols
  written without surrounding spaces.
- **A prompt that fails is reported on stderr and skipped**, so one bad
  prompt does not stop the others.

## Performance analysis

- **Reliability:** every output is valid JSON and follows the schema by
  construction, because only allowed tokens can be chosen.
- **Accuracy:** on my sample of 11 prompts (sums, greetings, string
  reversal, square roots, regex substitution), 10 were fully correct. This
  sample was used while tuning the prompt, so it is optimistic. The
  remaining error is a stray leading space in a replacement value.
  [TO FILL: score on a fresh set of prompts.]
- **Speed:** [TO FILL: total time for the full test file on my machine, and
  the 5 minute target].

## Challenges faced

- **Tokens do not match the JSON structure.** `{"` is a single token, and a
  function name is split over several tokens. The masks therefore work on
  the text each token would add, not on single characters.
- **Special tokenizer symbols.** Spaces and new lines appear as special
  characters in the vocabulary and had to be converted.
- **Values that never ended.** Models naturally close a string with a
  token that already contains the quote, which my first mask forbade. Any
  token containing a quote now ends the value.
- **Quotes and backslashes in values.** Building the JSON by concatenation
  broke on such values. Building a dict solved it.
- **Small model limits.** The model sometimes copies a literal from the
  request instead of writing a regex pattern. Few-shot examples improved
  this a lot but cannot guarantee it.
- **Speed.** Reloading the model for each prompt was the main cost.

## Testing strategy

- Run the program on the provided examples and check the output file.
- Check by script that the file is valid JSON, that every object has
  exactly `prompt`, `name` and `parameters`, and that parameter names and
  types match the definitions.
- Test the masks without the model by listing the allowed token texts for
  given partial values (for example `""`, `"12"`, `"12."`).
- Edge cases: invalid or missing input files, empty strings, negative and
  decimal numbers, values containing quotes or backslashes, and functions
  with several parameters.
- [TO FILL: describe your unit tests if you add some.]

## Limitations

- A double quote cannot appear inside a generated string value.
- Only `number` and `string` parameter types are handled.
  [UPDATE if other types are added.]
- A prompt for which generation fails is skipped and does not appear in the
  output file.

## Resources

- Qwen3 model card: https://huggingface.co/Qwen/Qwen3-0.6B
- JSON specification (RFC 8259): https://www.rfc-editor.org/rfc/rfc8259
- Python documentation: `json`, `pathlib`, `typing`
- pydantic documentation: https://docs.pydantic.dev
- Articles on constrained decoding and structured generation.
  [ADD the ones you actually read.]

**Use of AI.** [TO FILL, be precise and honest.] For example: AI was used as
a tutor to explain the generation pipeline and constrained decoding, to
review my code for bugs, to help draft this README and to suggest prompt
wording. The generation loop, the masks and the prompt were written and
tested by me, and I can explain every part of them.

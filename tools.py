"""Your tools. This is the file you will edit most.

A tool is a plain function plus one entry in the TOOLS list below.

To add a tool:
  1. Write a function. It takes plain arguments and returns a sentence.
  2. Add an entry to TOOLS: the function, a description, and one line per argument.

The description is what the model reads to decide when to use the tool, so write
it the way you would explain the tool to a new teammate.
"""

from pathlib import Path

NOTES = Path(__file__).parent / "notes.txt"


def count_words(text):
    count = len(text.split())
    return f"That text has {count} words."


def save_note(text):
    with open(NOTES, "a") as file:
        file.write(text.strip() + "\n")
    return f"Saved the note: {text.strip()}"


TOOLS = [
    {
        "function": count_words,
        "description": "Count the words in a piece of text. Use this whenever the "
                       "user asks how many words something has; do not count yourself.",
        "arguments": {"text": "The exact text to count, with nothing added or removed."},
    },
    {
        "function": save_note,
        "description": "Save a short note to the user's notes file so it is kept "
                       "after the chat ends. Use only when the user asks to save "
                       "or remember something.",
        "arguments": {"text": "The note to save, as one sentence."},
        "ask_first": True,  # the agent asks the human before running this tool
    },
]


def find_tool(name):
    for tool in TOOLS:
        if tool["function"].__name__ == name:
            return tool
    return None


def run_tool(name, arguments):
    """Run one tool. ALWAYS returns a string, even when something goes wrong.

    A problem is sent back to the model as a sentence, so it can fix its own
    mistake and try again. The agent never crashes because of a tool.
    """
    tool = find_tool(name)
    if tool is None:
        names = ", ".join(t["function"].__name__ for t in TOOLS)
        return f"Error: there is no tool called '{name}'. The tools are: {names}."
    try:
        return str(tool["function"](**arguments))
    except Exception as error:
        return f"Error: {name} failed: {error}"

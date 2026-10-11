"""The model layer: one function, chat(), in front of every provider.

    reply = chat(messages, tools, instructions)

    reply["text"]         what the model said
    reply["tool_calls"]   [{"id": "...", "name": "count_words", "arguments": {...}}]
    reply["usage"]        {"input": 12, "output": 5}

Messages are plain dicts, the same for every provider:

    {"role": "user", "text": "..."}
    {"role": "assistant", "text": "...", "tool_calls": [...]}
    {"role": "tool", "id": "...", "name": "...", "text": "..."}

model_anthropic.py and model_openai.py translate these to each provider's format.
"""

import config

_warned = []


def chat(messages, tools=(), instructions=""):
    provider = pick_provider()
    if provider == "fake":
        return fake_chat(messages, tools)
    if provider == "anthropic":
        import model_anthropic
        return model_anthropic.chat(messages, tools, instructions)
    import model_openai
    return model_openai.chat(messages, tools, instructions)


def ask(text, instructions=""):
    """One question, one answer, no tools. Used by the files in patterns/."""
    return chat([{"role": "user", "text": text}], [], instructions)["text"]


def pick_provider():
    """The provider from .env, or "fake" when that provider has no key yet."""
    provider = config.PROVIDER
    if provider not in config.PROVIDERS:
        raise ValueError(f"PROVIDER is '{provider}'. Use one of: {', '.join(config.PROVIDERS)}")
    if provider == "fake" or config.api_key(provider):
        return provider
    if not _warned:
        _warned.append(True)
        print(f"No {config.KEY_NAMES[provider]} found. Using the fake model. "
              f"Add a key to .env to use a real one.")
    return "fake"


def make_reply(text, tool_calls=(), input_tokens=0, output_tokens=0, raw=None):
    return {"text": text, "tool_calls": list(tool_calls),
            "usage": {"input": input_tokens, "output": output_tokens}, "raw": raw}


def to_schema(tool):
    """Turn one entry of TOOLS into the JSON schema that providers expect."""
    types = tool.get("types", {})
    properties = {}
    for name, description in tool["arguments"].items():
        properties[name] = {"type": types.get(name, "string"), "description": description}
    return {"type": "object", "properties": properties, "required": list(properties)}


FAKE_VALUES = {"integer": 1, "number": 1.0, "boolean": True}


def fake_chat(messages, tools):
    """A pretend model: no key, no network, no cost, and the same answer every time.

    It calls the first tool once, then answers using the tool's result. That is
    enough to prove the loop, the tools and the session log all work.
    """
    last = messages[-1]
    if last["role"] == "tool":
        return make_reply(f"(fake model) The {last['name']} tool said: {last['text']}")
    if not tools:
        return make_reply(f"(fake model) You said: {last['text']}")
    tool = tools[0]
    types = tool.get("types", {})
    arguments = {}
    for name in tool["arguments"]:
        arguments[name] = FAKE_VALUES.get(types.get(name, "string"), last["text"])
    call = {"id": f"call_{len(messages)}", "name": tool["function"].__name__,
            "arguments": arguments}
    return make_reply("", [call])

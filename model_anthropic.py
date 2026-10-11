"""Claude, through Anthropic's official package. Called by model.chat()."""

import anthropic

import config
from model import make_reply, to_schema


def chat(messages, tools, instructions):
    client = anthropic.Anthropic(api_key=config.api_key("anthropic"))
    request = {"model": config.MODEL, "max_tokens": 16000,
               "messages": to_anthropic(messages)}
    if instructions:
        request["system"] = instructions
    if tools:
        request["tools"] = [
            {"name": tool["function"].__name__, "description": tool["description"],
             "input_schema": to_schema(tool)}
            for tool in tools
        ]
    response = client.messages.create(**request)

    text, calls, blocks = "", [], []
    for block in response.content:
        if block.type == "text" and block.text:
            text += block.text
            blocks.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            calls.append({"id": block.id, "name": block.name, "arguments": block.input})
            blocks.append({"type": "tool_use", "id": block.id, "name": block.name,
                           "input": block.input})
        elif block.type == "thinking":
            blocks.append({"type": "thinking", "thinking": block.thinking,
                           "signature": block.signature})
        elif block.type == "redacted_thinking":
            blocks.append({"type": "redacted_thinking", "data": block.data})
    if response.stop_reason == "refusal" and not text:
        text = "The model declined this request."
    # Claude needs its own blocks sent back unchanged on the next step, so keep them.
    raw = {"provider": "anthropic", "content": blocks}
    return make_reply(text, calls, response.usage.input_tokens,
                      response.usage.output_tokens, raw)


def to_anthropic(messages):
    """Translate our plain messages into Anthropic's format."""
    out = []
    for message in messages:
        if message["role"] == "user":
            out.append({"role": "user", "content": message["text"]})
        elif message["role"] == "assistant":
            out.append({"role": "assistant", "content": assistant_blocks(message)})
        else:
            result = {"type": "tool_result", "tool_use_id": message["id"],
                      "content": message["text"] or "(empty)"}
            # All results for one step must travel together in one user message.
            if out and out[-1]["role"] == "user" and isinstance(out[-1]["content"], list):
                out[-1]["content"].append(result)
            else:
                out.append({"role": "user", "content": [result]})
    return out


def assistant_blocks(message):
    raw = message.get("raw")
    if raw and raw.get("provider") == "anthropic" and raw["content"]:
        return raw["content"]
    blocks = []
    if message["text"]:
        blocks.append({"type": "text", "text": message["text"]})
    for call in message["tool_calls"]:
        blocks.append({"type": "tool_use", "id": call["id"], "name": call["name"],
                       "input": call["arguments"]})
    return blocks or [{"type": "text", "text": "(no reply)"}]

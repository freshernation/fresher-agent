"""OpenAI, and any provider with an OpenAI-style endpoint. Called by model.chat().

PROVIDER=openai       uses OPENAI_API_KEY and OpenAI's own address.
PROVIDER=compatible   uses COMPATIBLE_API_KEY and COMPATIBLE_BASE_URL. This is how
                      DeepSeek, Qwen, Kimi, GLM and many others are reached.
"""

import json

from openai import OpenAI

import config
from model import make_reply, to_schema


def chat(messages, tools, instructions):
    provider = config.PROVIDER
    if not config.MODEL:
        raise ValueError("Set MODEL in .env to the model name your provider uses.")
    if provider == "compatible":
        if not config.get("COMPATIBLE_BASE_URL"):
            raise ValueError("Set COMPATIBLE_BASE_URL in .env to your provider's address.")
        client = OpenAI(api_key=config.api_key(provider),
                        base_url=config.get("COMPATIBLE_BASE_URL"))
    else:
        client = OpenAI(api_key=config.api_key(provider))

    request = {"model": config.MODEL, "messages": to_openai(messages, instructions)}
    if tools:
        request["tools"] = [
            {"type": "function",
             "function": {"name": tool["function"].__name__,
                          "description": tool["description"],
                          "parameters": to_schema(tool)}}
            for tool in tools
        ]
    response = client.chat.completions.create(**request)
    message = response.choices[0].message

    calls = []
    for call in message.tool_calls or []:
        try:
            arguments = json.loads(call.function.arguments or "{}")
        except ValueError:
            arguments = {}  # the tool will report the missing arguments to the model
        calls.append({"id": call.id, "name": call.function.name, "arguments": arguments})
    usage = response.usage
    return make_reply(message.content or "", calls,
                      usage.prompt_tokens if usage else 0,
                      usage.completion_tokens if usage else 0)


def to_openai(messages, instructions):
    """Translate our plain messages into the OpenAI chat format."""
    out = []
    if instructions:
        out.append({"role": "system", "content": instructions})
    for message in messages:
        if message["role"] == "user":
            out.append({"role": "user", "content": message["text"]})
        elif message["role"] == "tool":
            out.append({"role": "tool", "tool_call_id": message["id"],
                        "content": message["text"]})
        else:
            turn = {"role": "assistant", "content": message["text"] or None}
            if message["tool_calls"]:
                turn["tool_calls"] = [
                    {"id": call["id"], "type": "function",
                     "function": {"name": call["name"],
                                  "arguments": json.dumps(call["arguments"])}}
                    for call in message["tool_calls"]
                ]
            out.append(turn)
    return out

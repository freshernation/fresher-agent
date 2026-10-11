"""Offline tests. They use the fake model, so they need no key and cost nothing.

    python test_agent.py
"""

import contextlib
import importlib
import io
import tempfile
from pathlib import Path

import config

config.PROVIDER = "fake"  # before anything else, so no test can reach a real model

import agent
import model
import model_anthropic
import model_openai
import session
import tools

session.FOLDER = Path(tempfile.mkdtemp())
tools.NOTES = session.FOLDER / "notes.txt"

YES = lambda name, arguments: True
NO = lambda name, arguments: False


def quiet_run(session_id, text, approve=YES):
    with contextlib.redirect_stdout(io.StringIO()):
        return agent.run(session_id, text, approve)


def test_loop_calls_a_tool_then_answers():
    session_id = session.new_session()
    answer = quiet_run(session_id, "one two three")
    assert "3 words" in answer
    kinds = [event["type"] for event in session.get_events(session_id)]
    assert kinds == ["user", "model", "tool_result", "model"]


def test_max_steps_stops_a_loop_that_never_finishes():
    def always_calls_a_tool(messages, tools_list, instructions):
        call = {"id": f"c{len(messages)}", "name": "count_words", "arguments": {"text": "a"}}
        return model.make_reply("", [call])

    real_chat, real_steps = model.chat, config.MAX_STEPS
    model.chat, config.MAX_STEPS = always_calls_a_tool, 3
    try:
        session_id = session.new_session()
        answer = quiet_run(session_id, "go")
    finally:
        model.chat, config.MAX_STEPS = real_chat, real_steps
    assert answer.startswith("Stopped after 3 steps")
    assert session.get_events(session_id)[-1]["type"] == "stop"


def test_run_tool_always_returns_a_string():
    assert "no tool called" in tools.run_tool("missing", {})
    assert tools.run_tool("count_words", {"wrong": 1}).startswith("Error:")
    assert tools.run_tool("count_words", {"text": None}).startswith("Error:")


def test_ask_first_blocks_a_tool_when_the_human_says_no():
    def wants_to_save(messages, tools_list, instructions):
        if messages[-1]["role"] == "tool":
            return model.make_reply("done")
        return model.make_reply("", [{"id": "c1", "name": "save_note",
                                      "arguments": {"text": "secret"}}])

    real_chat, model.chat = model.chat, wants_to_save
    try:
        session_id = session.new_session()
        quiet_run(session_id, "save it", approve=NO)
        assert not tools.NOTES.exists()
        results = [e for e in session.get_events(session_id) if e["type"] == "tool_result"]
        assert "said no" in results[0]["text"]
        quiet_run(session.new_session(), "save it", approve=YES)
        assert tools.NOTES.read_text() == "secret\n"
    finally:
        model.chat = real_chat


def test_a_run_cut_off_before_its_tool_ran_can_be_resumed():
    session_id = session.new_session()
    session.emit(session_id, {"type": "user", "text": "one two"})
    session.emit(session_id, {"type": "model", "text": "", "raw": None, "tool_calls": [
        {"id": "c1", "name": "count_words", "arguments": {"text": "one two"}}]})
    quiet_run(session_id, "thanks")
    kinds = [event["type"] for event in session.get_events(session_id)]
    assert kinds[:4] == ["user", "model", "tool_result", "user"]


def test_an_unreadable_log_line_is_skipped():
    session_id = session.new_session()
    session.emit(session_id, {"type": "user", "text": "hi"})
    with open(session.path(session_id), "a") as file:
        file.write("not json\n")
    with contextlib.redirect_stdout(io.StringIO()):
        assert len(session.get_events(session_id)) == 1


MESSAGES = [
    {"role": "user", "text": "hi"},
    {"role": "assistant", "text": "", "tool_calls": [
        {"id": "a", "name": "count_words", "arguments": {"text": "x"}},
        {"id": "b", "name": "count_words", "arguments": {"text": "y"}}]},
    {"role": "tool", "id": "a", "name": "count_words", "text": "1"},
    {"role": "tool", "id": "b", "name": "count_words", "text": "1"},
]


def test_messages_convert_to_anthropic_format():
    out = model_anthropic.to_anthropic(MESSAGES)
    assert [m["role"] for m in out] == ["user", "assistant", "user"]
    assert [block["type"] for block in out[1]["content"]] == ["tool_use", "tool_use"]
    assert [block["tool_use_id"] for block in out[2]["content"]] == ["a", "b"]


def test_messages_convert_to_openai_format():
    out = model_openai.to_openai(MESSAGES, "be brief")
    assert [m["role"] for m in out] == ["system", "user", "assistant", "tool", "tool"]
    assert out[2]["tool_calls"][0]["function"]["arguments"] == '{"text": "x"}'
    assert out[3]["tool_call_id"] == "a"


def test_tool_schema():
    schema = model.to_schema({"arguments": {"text": "words", "times": "how many"},
                              "types": {"times": "integer"}})
    assert schema["properties"]["text"] == {"type": "string", "description": "words"}
    assert schema["properties"]["times"]["type"] == "integer"
    assert schema["required"] == ["text", "times"]


def test_every_pattern_runs():
    for name in ("chaining", "routing", "parallel", "orchestrator", "evaluator"):
        with contextlib.redirect_stdout(io.StringIO()):
            importlib.import_module(f"patterns.{name}").main()


if __name__ == "__main__":
    tests = [value for name, value in list(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print(f"[ok]   {test.__name__}")
    print(f"\n{len(tests)} tests passed.")

"""The agent loop. This is the whole agent.

    1. Send the conversation to the model.
    2. If the model answered, we are done.
    3. If the model asked for tools, run them and add the results.
    4. Go back to 1, at most MAX_STEPS times.

Every event is written to the session log as it happens, and the loop reads the
log at the start. Nothing else is remembered.
"""

import config
import model
import session
from tools import TOOLS, find_tool, run_tool

INSTRUCTIONS = (config.HERE / "instructions.md").read_text()


def ask_human(name, arguments):
    answer = input(f"  The agent wants to run {name}({arguments}). Allow? [y/n] ")
    return answer.strip().lower().startswith("y")


def run(session_id, user_text, approve=ask_human):
    """Answer one user message. Returns the agent's final text."""
    messages = session.to_messages(session.get_events(session_id))
    run_waiting_tools(session_id, messages, approve)  # only if the last run was cut off
    record(session_id, messages, {"type": "user", "text": user_text})

    for step in range(1, config.MAX_STEPS + 1):
        reply = model.chat(messages, TOOLS, INSTRUCTIONS)
        record(session_id, messages, {"type": "model", "text": reply["text"],
                                      "tool_calls": reply["tool_calls"],
                                      "usage": reply["usage"], "raw": reply["raw"]})
        if not reply["tool_calls"]:
            print(f"  step {step}: the model answered")
            return reply["text"]
        names = ", ".join(call["name"] for call in reply["tool_calls"])
        print(f"  step {step}: the model asked for {names}")
        run_waiting_tools(session_id, messages, approve)

    record(session_id, messages, {"type": "stop", "reason": "max_steps"})
    return (f"Stopped after {config.MAX_STEPS} steps without a final answer. "
            f"Raise MAX_STEPS in .env if the task needs more.")


def record(session_id, messages, event):
    """Write an event to the log and add it to the conversation."""
    session.emit(session_id, event)
    messages.extend(session.to_messages([event]))


def waiting_calls(messages):
    """Tool calls from the model's last turn that have no result yet."""
    answered = set()
    for message in reversed(messages):
        if message["role"] == "tool":
            answered.add(message["id"])
        elif message["role"] == "assistant":
            return [call for call in message["tool_calls"] if call["id"] not in answered]
        else:
            break
    return []


def run_waiting_tools(session_id, messages, approve):
    for call in waiting_calls(messages):
        name, arguments = call["name"], call["arguments"]
        tool = find_tool(name)
        if tool and tool.get("ask_first"):
            approved = approve(name, arguments)
            session.emit(session_id, {"type": "approval", "name": name,
                                      "approved": approved})
        else:
            approved = True
        if approved:
            result = run_tool(name, arguments)
        else:
            result = "The user said no to this action. Do not retry it; ask what they want."
        print(f"    {name}({arguments}) -> {result}")
        record(session_id, messages, {"type": "tool_result", "id": call["id"],
                                      "name": name, "text": result})

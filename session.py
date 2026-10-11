"""The session log: everything that happened, one line per event.

Each session is a file in sessions/. Lines are only ever added, never changed.
The agent keeps nothing in memory between runs, so a session can be continued
at any time from its file.

Event types: user, model, tool_result, approval, stop.
"""

import json
import uuid
from datetime import datetime

import config

FOLDER = config.HERE / "sessions"


def path(session_id):
    return FOLDER / f"{session_id}.jsonl"


def new_session():
    FOLDER.mkdir(exist_ok=True)
    session_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:4]
    path(session_id).touch()
    return session_id


def emit(session_id, event):
    """Add one event to the end of the log."""
    line = {"time": datetime.now().isoformat(timespec="seconds"), **event}
    with open(path(session_id), "a") as file:
        file.write(json.dumps(line) + "\n")


def get_events(session_id):
    events = []
    for number, line in enumerate(path(session_id).read_text().splitlines(), start=1):
        try:
            events.append(json.loads(line))
        except ValueError:
            print(f"Warning: skipped unreadable line {number} in {path(session_id).name}")
    return events


def to_messages(events):
    """Rebuild the message list the model needs from the logged events."""
    messages = []
    for event in events:
        if event["type"] == "user":
            messages.append({"role": "user", "text": event["text"]})
        elif event["type"] == "model":
            messages.append({"role": "assistant", "text": event["text"],
                             "tool_calls": event["tool_calls"], "raw": event.get("raw")})
        elif event["type"] == "tool_result":
            messages.append({"role": "tool", "id": event["id"], "name": event["name"],
                             "text": event["text"]})
    return messages

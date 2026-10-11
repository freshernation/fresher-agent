"""Check what is working and what is not.

    python check.py

Prints one line per part. Run it after setup and after every change you make.
"""

import contextlib
import io
import sys
import tempfile
from pathlib import Path

failed = []


def report(status, text):
    print(f"[{status}]".ljust(7) + text)
    if status == "fail":
        failed.append(text)


def check_python():
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info >= (3, 10):
        report("ok", f"Python {version}")
    else:
        report("fail", f"Python {version} is too old. Install 3.10 or newer.")


def check_packages():
    try:
        import anthropic  # noqa: F401
        import openai  # noqa: F401
        report("ok", "packages installed")
    except ImportError as error:
        report("fail", f"{error}. Run the setup script again.")


def check_hello_agent():
    """Run the real loop against the fake model, in a throwaway folder."""
    import agent
    import config
    import session
    from tools import TOOLS

    report("ok", f"tools.py loads ({len(TOOLS)} tools)")
    real_provider, real_folder = config.PROVIDER, session.FOLDER
    config.PROVIDER, session.FOLDER = "fake", Path(tempfile.mkdtemp())
    try:
        session_id = session.new_session()
        with contextlib.redirect_stdout(io.StringIO()):
            answer = agent.run(session_id, "hello world", approve=lambda *_: False)
        events = session.get_events(session_id)
        steps = sum(1 for event in events if event["type"] == "model")
        calls = sum(1 for event in events if event["type"] == "tool_result")
        if answer and steps >= 2 and calls >= 1:
            report("ok", f"hello agent ran with the fake model ({steps} steps, {calls} tool call)")
            report("ok", "session log written and reloaded")
        else:
            report("fail", f"hello agent did not finish as expected: {answer!r}")
    finally:
        config.PROVIDER, session.FOLDER = real_provider, real_folder


def check_real_model():
    import config
    import model

    provider = config.PROVIDER
    if provider == "fake":
        report("skip", "real model: PROVIDER is fake in .env")
    elif not config.api_key(provider):
        report("skip", f"real model: no {config.KEY_NAMES[provider]} in .env yet")
    else:
        try:
            model.ask("Reply with the single word: ok")
            report("ok", f"real model answered ({provider}, {config.MODEL})")
        except Exception as error:
            report("fail", f"real model ({provider}, {config.MODEL}): {error}")


def main():
    check_python()
    check_packages()
    try:
        check_hello_agent()
        check_real_model()
    except Exception as error:
        report("fail", f"{type(error).__name__}: {error}")
    print()
    print("Something needs fixing. See the [fail] lines above." if failed
          else "All good. Try: python run.py \"How many words are in: the quick brown fox\"")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

"""Start the agent.

    python run.py                       chat in the terminal
    python run.py "one question"        ask once and exit
    python run.py --resume <session>    continue an earlier session
"""

import sys

import agent
import session


def answer(session_id, text):
    try:
        return agent.run(session_id, text)
    except Exception as error:
        return (f"Something went wrong talking to the model: {error}\n"
                f"Nothing is lost. Fix the problem, then run: "
                f"python run.py --resume {session_id}")


def main():
    args = sys.argv[1:]
    if args[:1] == ["--resume"]:
        if len(args) < 2 or not session.path(args[1]).exists():
            print("No such session. Look in the sessions/ folder for the names.")
            return 1
        session_id, args = args[1], args[2:]
    else:
        session_id = session.new_session()
    print(f"Session {session_id}")

    if args:
        print(answer(session_id, " ".join(args)))
        return 0

    print("Type a message and press Enter. Type 'quit' to stop.")
    while True:
        try:
            text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text in ("quit", "exit"):
            break
        if text:
            print("agent>", answer(session_id, text))
    print(f"\nContinue later with: python run.py --resume {session_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

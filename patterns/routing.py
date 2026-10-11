"""Pattern 2: routing.

Classify the input first, then send it to instructions written for that kind.

Use it when inputs fall into clear groups that need different handling.
                                               python -m patterns.routing
"""

from model import ask

ROUTES = {
    "refund": "You handle refund requests. Be brief and kind. Ask for the order number.",
    "technical": "You handle technical problems. Ask for the exact error message.",
    "general": "You answer general questions in one or two sentences.",
}


def run(message):
    label = ask("Classify this message. Reply with one word only: "
                f"refund, technical or general.\n\n{message}").strip().lower()
    if label not in ROUTES:  # never trust the label blindly
        label = "general"
    return label, ask(message, ROUTES[label])


def main():
    label, answer = run("My order arrived broken and I want my money back.")
    print(f"route: {label}\n{answer}")


if __name__ == "__main__":
    main()

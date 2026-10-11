"""Pattern 5: evaluator and optimizer.

One call writes a draft, another call reviews it, and the writer tries again
with the feedback. The loop stops when the reviewer is happy or the rounds run out.

Use it when you can say clearly what "good" means.
                                               python -m patterns.evaluator
"""

from model import ask

MAX_ROUNDS = 3


def run(task):
    draft = ask(task)
    for _ in range(MAX_ROUNDS):
        feedback = ask("Review this answer. If it is clear and correct, reply with "
                       f"only the word OK. Otherwise say what to fix.\n\n"
                       f"Task: {task}\n\nAnswer: {draft}")
        if feedback.strip().upper().startswith("OK"):
            break
        draft = ask(f"Task: {task}\n\nYour last answer: {draft}\n\n"
                    f"Feedback: {feedback}\n\nWrite an improved answer.")
    return draft


def main():
    print(run("Explain what an API key is to a ten-year-old in two sentences."))


if __name__ == "__main__":
    main()

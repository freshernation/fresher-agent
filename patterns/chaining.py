"""Pattern 1: prompt chaining.

Split a task into fixed steps. Each step uses the output of the one before, and
a plain-code check (a "gate") sits between steps so a bad result stops early.

Use it when the steps are always the same.     python -m patterns.chaining
"""

from model import ask


def run(topic):
    outline = ask(f"Write a 3-point outline for a short post about: {topic}")
    if len(outline.strip()) < 10:  # the gate
        return "Stopped: the outline was too short to use."
    return ask(f"Write a short post that follows this outline:\n{outline}")


def main():
    print(run("why tests make code easier to change"))


if __name__ == "__main__":
    main()

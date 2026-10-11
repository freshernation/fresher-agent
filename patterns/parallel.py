"""Pattern 3: parallelization.

Sectioning: split one job into independent parts and run them at the same time.
Voting:     ask the same question several times and count the answers.

Use it when the parts do not depend on each other.
                                               python -m patterns.parallel
"""

from concurrent.futures import ThreadPoolExecutor

from model import ask


def review(code):
    """Sectioning: three reviewers, each looking at one thing."""
    aspects = ["bugs", "readability", "security"]
    prompts = [f"Review this code for {aspect} only. One sentence.\n\n{code}"
               for aspect in aspects]
    with ThreadPoolExecutor() as pool:
        answers = list(pool.map(ask, prompts))
    return dict(zip(aspects, answers))


def is_safe(text, voters=3):
    """Voting: the text is safe only if most voters say yes."""
    prompt = f"Is this message safe to show a child? Reply yes or no only.\n\n{text}"
    with ThreadPoolExecutor() as pool:
        votes = list(pool.map(ask, [prompt] * voters))
    yes = sum(1 for vote in votes if vote.strip().lower().startswith("yes"))
    return yes > voters / 2


def main():
    for aspect, answer in review("def add(a, b): return a - b").items():
        print(f"{aspect}: {answer}")
    print("safe:", is_safe("Let's bake a cake."))


if __name__ == "__main__":
    main()

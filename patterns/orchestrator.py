"""Pattern 4: orchestrator and workers.

One model call plans the subtasks, a worker call does each one, and a final
call joins the results. Unlike parallel.py, the model decides the subtasks.

Use it when you cannot know the subtasks before you see the request.
                                               python -m patterns.orchestrator
"""

from model import ask

MAX_SUBTASKS = 3


def run(task):
    plan = ask(f"Break this task into at most {MAX_SUBTASKS} subtasks, "
               f"one per line, no numbering.\n\n{task}")
    subtasks = [line.strip() for line in plan.splitlines() if line.strip()]
    subtasks = subtasks[:MAX_SUBTASKS]
    results = [ask(f"Do this subtask and report the result briefly:\n{subtask}")
               for subtask in subtasks]
    joined = "\n".join(f"- {subtask}: {result}"
                       for subtask, result in zip(subtasks, results))
    return ask(f"Task: {task}\n\nResults of the subtasks:\n{joined}\n\n"
               f"Write the final answer.")


def main():
    print(run("Compare tea and coffee for someone who wants to sleep better."))


if __name__ == "__main__":
    main()

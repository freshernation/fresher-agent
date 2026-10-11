# Instructions for AI coding assistants

This repository is Fresher Agent: a small template for building an AI agent. Its
users are beginners. Keep every change as simple as the code already here.

## Map

| File | Role | Edit it? |
|---|---|---|
| `tools.py` | The tools and `run_tool` | Yes, this is where most changes go |
| `instructions.md` | The system prompt | Yes |
| `.env` | Provider, model, keys, `MAX_STEPS` | Yes. Never print or commit it |
| `agent.py` | The loop | Only when asked to change the loop |
| `model.py`, `model_anthropic.py`, `model_openai.py` | Provider layer | Only to add or fix a provider |
| `session.py` | Append-only session log | Rarely |
| `config.py` | Reads `.env` | Only to add a setting |
| `patterns/` | Standalone workflow examples | Add new ones freely |
| `test_agent.py` | Offline tests | Add a test with every behaviour change |

## House rules

1. **Style.** Plain functions and dicts. No classes, decorators, type hints or
   `async`. Keep each file near 100 lines. Match the comments already in the file.
2. **No new dependencies** unless the user asks. `requirements.txt` has two.
3. **Tools return a sentence.** Never `None`, never a raw exception. `run_tool`
   turns failures into text for the model; keep that guarantee.
4. **Anything hard to undo gets `"ask_first": True`.** Sending, deleting, paying,
   overwriting.
5. **The session log is append-only.** Never rewrite or delete lines.
6. **Keys stay in `config.py` and the `model_*.py` files.** Never read a key in a tool.
7. **Prefer the simplest design.** If one model call or a file in `patterns/`
   solves the request, do that and do not grow the loop.

## Common tasks

**Add a tool**

1. Write a function in `tools.py` that takes plain arguments and returns a sentence.
2. Add an entry to `TOOLS` with `function`, `description` and `arguments`. Use
   `types` for non-text arguments and `ask_first` for risky ones.
3. Write the description as a prompt: when to use it, with an example argument.
4. Add a test to `test_agent.py` that calls `tools.run_tool(name, arguments)`.

**Change provider or model:** edit `.env` only. See `docs/GUIDE.md#providers`.

**Change behaviour:** edit `instructions.md`.

**Add a workflow:** copy a file in `patterns/`, keep it standalone, use only
`model.ask`, and add its name to `test_every_pattern_runs`.

## Finish every change with

```bash
.venv/bin/python check.py
.venv/bin/python test_agent.py
```

On Windows use `.venv\Scripts\python`. Both must pass. They run offline against
the fake model and cost nothing. If `.venv` is missing, run the setup script
(`sh setup-fresher-agent.sh` or `setup-fresher-agent.bat`) first.

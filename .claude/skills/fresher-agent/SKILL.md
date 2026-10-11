---
name: fresher-agent
description: Work on a Fresher Agent project. Use when adding or changing a tool, switching model provider, editing the agent's instructions, adding a workflow pattern, or debugging why the agent misbehaves in a repository that contains agent.py, tools.py and check.py.
---

# Working on a Fresher Agent project

The users of this template are beginners. Make the smallest change that works and
keep the code as plain as what is already there.

## First

1. Read `AGENTS.md` in the project root. It has the file map and the house rules.
2. If there is no `.venv` folder, run the setup script: `sh setup-fresher-agent.sh`
   (Windows: `setup-fresher-agent.bat`).
3. Run `.venv/bin/python check.py` to see what currently works.

## Add a tool

1. In `tools.py`, write a plain function. Plain arguments in, a sentence out.
2. Add an entry to `TOOLS`:

   ```python
   {
       "function": get_weather,
       "description": "Get today's weather for a city. Use when the user asks "
                      "about weather, temperature or rain.",
       "arguments": {"city": "City name in English, for example Chennai"},
   },
   ```

3. Non-text arguments: add `"types": {"days": "integer"}` (`number`, `boolean`).
4. If the tool sends, deletes, pays or overwrites: add `"ask_first": True`.
5. Add a test in `test_agent.py` using `tools.run_tool("get_weather", {...})`.
6. Never read an API key inside a tool. If the tool needs a secret, add a setting
   to `.env.example`, read it with `config.get("NAME")`, and tell the user to fill it in.

## Switch provider or model

Edit `.env` only. `PROVIDER` is `anthropic`, `openai`, `compatible` or `fake`.
For DeepSeek, Qwen, Kimi and GLM use `compatible` with `COMPATIBLE_BASE_URL`,
`COMPATIBLE_API_KEY` and `MODEL`. Addresses are in `docs/GUIDE.md`. Never print
the contents of `.env`.

## Change how the agent behaves

Edit `instructions.md`. If the agent picks the wrong tool, fix that tool's
`description` in `tools.py` before touching anything else.

## Add a workflow

Before growing the loop, check whether a file in `patterns/` fits. To add one,
copy the closest file, keep it standalone with a `main()` function, use only
`model.ask`, and add its name to `test_every_pattern_runs` in `test_agent.py`.

## Debug

Read the newest file in `sessions/`. It lists every model reply, tool call and
tool result in order. Continue a chat with `python run.py --resume <name>`.

## Always finish with

```bash
.venv/bin/python check.py
.venv/bin/python test_agent.py
```

Both must pass before you report the work as done. Show the user the output.

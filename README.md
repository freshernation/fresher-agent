# Fresher Agent

A small, readable starting point for building an AI agent. No framework to learn:
the whole agent is a few short Python files that you own and can read in one sitting.

It follows Anthropic's [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
and [Managed agents](https://www.anthropic.com/engineering/managed-agents) articles.

## 1. Set up

You need [Python 3.10 or newer](https://www.python.org/downloads/). Download this
repository (green **Code** button, then **Download ZIP**, or `git clone`), open a
terminal in the folder, and run one command:

| | |
|---|---|
| Mac or Linux | `sh setup-fresher-agent.sh` |
| Windows | `setup-fresher-agent.bat` |

It installs everything and ends with a checklist of what works:

```
[ok]   Python 3.12
[ok]   packages installed
[ok]   tools.py loads (2 tools)
[ok]   hello agent ran with the fake model (2 steps, 1 tool call)
[ok]   session log written and reloaded
[skip] real model: no ANTHROPIC_API_KEY in .env yet
```

Run `python check.py` to see this checklist again at any time.

## 2. Run it

```bash
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python run.py "How many words are in: the quick brown fox"
```

It works straight away with **no API key**, using a built-in fake model, so you can
see the agent take a step, call a tool, and answer. `python run.py` on its own
starts a chat.

## 3. Use a real model

Open `.env`, paste your key next to `ANTHROPIC_API_KEY=`, and run it again.
To use OpenAI, DeepSeek, Qwen, Kimi or GLM instead, change `PROVIDER` in the same
file. [The guide](docs/GUIDE.md#providers) has the exact lines for each.

## 4. Make it yours

| To change | Edit |
|---|---|
| What the agent can do | `tools.py`: write a function, add it to `TOOLS` |
| How the agent behaves | `instructions.md` |
| Which model it uses, and its step limit | `.env` |
| How the loop itself works | `agent.py` (about 80 lines) |

After any change, run `python check.py` and `python test_agent.py`.

## What is in the box

| File | What it is |
|---|---|
| `agent.py` | The loop: ask the model, run its tools, repeat |
| `tools.py` | The tools, and the one function that runs them safely |
| `model.py` | One `chat()` function in front of every provider |
| `session.py` | A log of every step, so any chat can be continued later |
| `patterns/` | Five simpler designs to try before you reach for an agent |
| `docs/GUIDE.md` | The detailed guide |
| `docs/ROADMAP.md` | What was left out on purpose, and how to add it |
| `AGENTS.md` | Instructions for AI coding assistants working in this repo |

## Using an AI coding assistant

Open this folder in Claude Code, Codex or Cursor and ask for what you want, for
example "add a tool that looks up the weather". The assistant reads `AGENTS.md`
and follows the same rules you would.

In Claude Code you can also start a fresh project from anywhere:

```
/plugin marketplace add freshernation/fresher-agent
/plugin install fresher-agent@freshernation
/fresher-agent:new my-agent
```

## License

[MIT](LICENSE). Use it for anything, personal or commercial, and change it however you like.

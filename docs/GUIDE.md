# The Fresher Agent guide

The [README](../README.md) gets you running in one page. This guide explains every
part, so you can change any of it with confidence.

- [What an agent is](#what-an-agent-is)
- [Do you need an agent at all?](#do-you-need-an-agent-at-all)
- [The loop](#the-loop)
- [Tools](#tools)
- [Instructions](#instructions)
- [Providers](#providers)
- [The session log](#the-session-log)
- [The five patterns](#the-five-patterns)
- [Checking and testing](#checking-and-testing)
- [When something goes wrong](#when-something-goes-wrong)
- [How this follows the Anthropic articles](#how-this-follows-the-anthropic-articles)

## What an agent is

A language model on its own can only write text. An **agent** is a model that is
allowed to ask for actions ("tools"), sees what each action returned, and decides
what to do next, in a loop, until the job is done.

That is all. In this repository the loop is `agent.py`, the actions are in
`tools.py`, and the model is reached through `model.py`.

## Do you need an agent at all?

Often not. Start with the simplest thing that works:

1. **One model call.** Summarise, classify, rewrite, answer. Use `model.ask(text)`.
2. **A workflow.** A few model calls joined by ordinary code that you control.
   See [the five patterns](#the-five-patterns).
3. **An agent.** Only when you cannot know the steps in advance, and the model
   has to decide them.

Each step up costs more time and money per request and is harder to predict. Move
up only when the simpler option has been tried and measurably falls short.

## The loop

Open `agent.py`. The function `run(session_id, user_text)` does this:

1. Rebuilds the conversation from the session log.
2. Adds the user's message.
3. Sends the conversation, the tools and the instructions to the model.
4. If the model replied with text and no tool calls, returns that text.
5. Otherwise runs each tool the model asked for and adds the results.
6. Goes back to step 3.

Three things keep the loop safe:

- **A step limit.** After `MAX_STEPS` model calls (10 by default, set in `.env`)
  the loop stops and says so.
- **A human check.** A tool marked `"ask_first": True` runs only after you type `y`.
- **Tool errors become text.** A tool that fails never crashes the agent. The
  error is sent to the model as a sentence, so it can correct itself.

Every step is printed as it happens, so you can always see what the agent is doing:

```
  step 1: the model asked for count_words
    count_words({'text': 'the quick brown fox'}) -> That text has 4 words.
  step 2: the model answered
```

## Tools

A tool is a plain function plus one entry in the `TOOLS` list in `tools.py`.

```python
def get_weather(city):
    return f"It is sunny in {city}."

TOOLS = [
    {
        "function": get_weather,
        "description": "Get today's weather for a city. Use when the user asks "
                       "about weather, temperature or rain.",
        "arguments": {"city": "City name in English, for example Chennai"},
    },
]
```

Rules for the function:

- **Return a sentence.** The model reads the result, so `"No city called Xyz was
  found."` is far more useful than `None` or `-1`.
- **Take simple arguments.** Text, numbers, true or false.
- **Do one thing.** Two small tools are easier for a model to use than one big one.

Options for the entry:

| Key | Meaning |
|---|---|
| `function` | The function to run. Its name is the tool's name. |
| `description` | When and why to use the tool. The model reads this. |
| `arguments` | One line of explanation per argument. |
| `types` | Optional. Arguments are text unless you say otherwise: `"types": {"count": "integer"}`. Other values: `"number"`, `"boolean"`. |
| `ask_first` | Optional. `True` makes the agent ask you before running the tool. Use it for anything that sends, deletes, spends or cannot be undone. |

### Writing a good description

The description is a prompt. Most "the agent used the wrong tool" problems are
fixed here, not in code.

- Say **when** to use the tool, not only what it does.
- Say what a good argument looks like, with an example.
- If two tools are similar, say how to choose between them.
- Design the arguments so mistakes are hard to make. For example, ask for a full
  date (`2026-10-11`) instead of "a date".
- Then test it: ask the agent ten different ways and read the printed steps.

## Instructions

`instructions.md` is the system prompt: standing orders the model receives with
every request. Write it in plain language. Say who the agent is for, what it
should and should not do, and how it should answer. Change it, run the agent,
read the result, and repeat.

## Providers

All settings live in `.env`. Pick one block.

**Anthropic (the default)**

```
PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
```

**OpenAI**

```
PROVIDER=openai
OPENAI_API_KEY=your-key
```

**Any OpenAI-style service**, including the major Chinese providers. Set the
provider's address, your key, and the model name:

```
PROVIDER=compatible
COMPATIBLE_API_KEY=your-key
COMPATIBLE_BASE_URL=https://api.deepseek.com
MODEL=deepseek-chat
```

| Provider | `COMPATIBLE_BASE_URL` |
|---|---|
| DeepSeek | `https://api.deepseek.com` |
| Qwen (Alibaba Cloud) | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| Kimi (Moonshot AI) | `https://api.moonshot.cn/v1` |
| GLM (Zhipu AI) | `https://open.bigmodel.cn/api/paas/v4` |

Addresses and model names change. If a call fails, check the provider's own
documentation for its current "OpenAI-compatible" address and model list.

**No key at all**

```
PROVIDER=fake
```

The fake model costs nothing and needs no network. It calls the first tool in
`TOOLS` once and then repeats the tool's result. It is also what the agent uses
automatically when the provider you chose has no key yet.

**Choosing a model.** Leave `MODEL=` blank for the provider's default
(`claude-opus-5-5` for Anthropic, `gpt-6-astra` for OpenAI), or set any model
name your provider offers. Smaller models are cheaper and faster; start with the
default and move down only after checking the answers are still good.

## The session log

Every chat is a file in `sessions/`, one line per event:

```json
{"time": "2026-10-11T09:23:56", "type": "user", "text": "the quick brown fox"}
{"time": "2026-10-11T09:23:56", "type": "model", "text": "", "tool_calls": [...]}
{"time": "2026-10-11T09:23:56", "type": "tool_result", "name": "count_words", "text": "That text has 4 words."}
{"time": "2026-10-11T09:23:57", "type": "model", "text": "It has 4 words.", "tool_calls": []}
```

Lines are only ever added. The agent keeps nothing in memory between runs: it
rebuilds the conversation from this file each time. That gives you two things.

- **You can continue any chat:** `python run.py --resume <session-name>`. If a run
  was cut off after the model asked for a tool but before the tool ran, the tool
  runs first when you resume.
- **You can see exactly what happened.** When the agent does something odd, open
  the file and read it.

Event types: `user`, `model`, `tool_result`, `approval`, `stop`.

## The five patterns

`patterns/` holds five small workflows. Each is about twenty lines, uses only
`model.ask`, and runs on its own. Try these before building an agent.

| Run | Pattern | Use it when |
|---|---|---|
| `python -m patterns.chaining` | Do step 1, check it, do step 2 | The steps are always the same |
| `python -m patterns.routing` | Classify, then use instructions for that kind | Inputs fall into clear groups |
| `python -m patterns.parallel` | Run independent parts at once, or vote | Parts do not depend on each other |
| `python -m patterns.orchestrator` | One call plans, workers do, one call joins | You cannot know the subtasks in advance |
| `python -m patterns.evaluator` | Write, review, rewrite | You can say clearly what "good" means |

With the fake model the output is only an echo; add a key to see them work.

## Checking and testing

- `python check.py` tells you what works: Python, packages, tools, the loop, the
  log, and (if you have a key) a real call to your model.
- `python test_agent.py` runs ten offline tests of the loop, the tools, the log
  and the provider translations. They never use a real model.

Run both after every change. When you add a tool, add a test for it next to the
others in `test_agent.py`.

## When something goes wrong

| You see | What to do |
|---|---|
| `Using the fake model` | No key for your provider. Add it to `.env`. |
| `Something went wrong talking to the model: ...` | Read the message: it comes from the provider. Usually a wrong key, model name or address. Your chat is saved; fix `.env` and resume. |
| `Stopped after 10 steps` | The task needs more steps (raise `MAX_STEPS`), or the agent is going in circles (improve a tool description). |
| `Error: there is no tool called ...` in the steps | The model made up a tool name. The agent tells it the real names and it recovers. |
| The agent picks the wrong tool | Rewrite that tool's `description`. |
| `[fail]` in `python check.py` | The line says what is wrong. Running the setup script again fixes most of them. |

## How this follows the Anthropic articles

From [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents):

| The article says | Where it is here |
|---|---|
| Call the model directly; avoid layers that hide prompts | `model.py` and `agent.py` are in your repo, in full |
| Use the simplest design that works | [Do you need an agent at all?](#do-you-need-an-agent-at-all) |
| The building block is a model with tools and memory | `tools.py`, `session.py` |
| Five workflow patterns | `patterns/` |
| Get ground truth from the environment at every step | Tool results are added on every turn of the loop |
| Pause for human feedback at checkpoints | `ask_first` |
| Always have a stopping condition | `MAX_STEPS` |
| Show the agent's steps | Every step is printed and logged |
| Tool definitions deserve as much care as prompts | `description` and `arguments` in `TOOLS` |

From [Managed agents](https://www.anthropic.com/engineering/managed-agents):

| The article says | Where it is here |
|---|---|
| Every tool sits behind one interface, `execute(name, input) -> string` | `run_tool(name, arguments)` in `tools.py` |
| The session is an append-only log kept outside the loop | `session.py` |
| The loop keeps no state, so it can be restarted from the log | `python run.py --resume` |
| A failed tool is reported to the model, not treated as a crash | `run_tool` |
| Keep credentials away from code the model drives | Keys are read only in `config.py` and the `model_*.py` files, never in tools |
| Do not build in assumptions about what the model cannot do | The loop adds no planning or prompting tricks of its own |

The article also describes sandboxes, credential vaults and on-demand containers.
Those are for hosted services running many agents; see [ROADMAP.md](ROADMAP.md).

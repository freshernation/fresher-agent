# What was left out, and how to add it

Fresher Agent is deliberately small. Everything below is a real part of
production agents and was left out so that a beginner can read the whole thing.

Each entry says what it is, why it is not here, and where it would connect. The
connection points already exist, so each one can be added later, or become its own
more advanced agent built on this one, without rewriting the core.

## Summary

| Left out | Connects at |
|---|---|
| [Sandbox](#sandbox) | a tool, behind `run_tool` |
| [Credential vault](#credential-vault) | `config.py` |
| [On-demand containers](#on-demand-containers) | a tool, behind `run_tool` |
| [Context compaction](#context-compaction) | `session.to_messages` |
| [Streaming](#streaming) | `model.chat` |
| [Sub-agents](#sub-agents) | `agent.run`, called as a tool |
| [Retrieval](#retrieval) | a tool |
| [MCP](#mcp) | the `TOOLS` list |
| [Web interface and deployment](#web-interface-and-deployment) | `run.py` |
| [Model-graded evaluations](#model-graded-evaluations) | `test_agent.py` |

## Sandbox

**What:** an isolated machine where the agent can run code and edit files without
being able to harm yours.
**Why not here:** the starter tools are ordinary functions you wrote. Nothing runs
code written by the model.
**How to add:** write a tool such as `run_python(code)` whose function sends the
code to a container or a hosted sandbox and returns the output as text. The loop
does not change, because every tool is already `name, arguments -> string`.
**Do not skip this** if you ever let the model write code that gets executed.

## Credential vault

**What:** a store that holds passwords and tokens outside the agent, and attaches
them to requests on the way out, so the model and its tools never see them.
**Why not here:** one API key in `.env` is enough for a single user on one laptop.
**How to add:** replace `config.api_key()` with a call to your vault. For tools
that call outside services, send requests through a proxy that adds the token.

## On-demand containers

**What:** starting a sandbox only when the agent first needs one, and replacing it
if it dies, without losing the conversation.
**Why not here:** there is no sandbox to start.
**How to add:** inside the sandbox tool, create the container on first use. If it
fails, return the failure as the tool's result; the model can retry, and the
session log is unaffected because it lives outside the container.

## Context compaction

**What:** shortening a long conversation so it still fits in the model's memory.
**Why not here:** short chats never fill it, and doing this badly loses facts.
**How to add:** `session.to_messages` is the one place that turns the log into what
the model sees. Summarise or trim there. The log file itself stays complete, so
nothing is ever lost for good.

## Streaming

**What:** showing the model's answer word by word as it is written.
**Why not here:** it roughly doubles the code in each provider file.
**How to add:** in `model_anthropic.py` and `model_openai.py`, switch to the
provider's streaming call, print text as it arrives, and return the same reply
dict at the end. Nothing outside those files needs to know.

## Sub-agents

**What:** an agent that hands part of its job to another agent.
**Why not here:** one loop solves most problems, and several agents are much
harder to debug.
**How to add:** write a tool whose function starts a new session and calls
`agent.run` with its own instructions, then returns the final text.

## Retrieval

**What:** letting the agent search your own documents.
**Why not here:** it needs a search index, which is a project of its own.
**How to add:** it is one more tool, `search_documents(query)`, that returns the
best matching passages as text. Start with plain keyword search over files.

## MCP

**What:** the Model Context Protocol, a standard way to plug in tools that other
people have built.
**Why not here:** it adds a second process and a protocol to learn.
**How to add:** connect to an MCP server at start-up, and add one entry to `TOOLS`
for each tool it offers, with a function that forwards the call.

## Web interface and deployment

**What:** a web page or chat app in front of the agent, running on a server.
**Why not here:** a terminal is enough to learn with.
**How to add:** `agent.run(session_id, text)` takes text and returns text. Call it
from a web framework's request handler in place of `run.py`. Give `approve` a
function that asks the user through your interface instead of the terminal.

## Model-graded evaluations

**What:** measuring answer quality across many example questions, using a model as
the judge.
**Why not here:** the included tests check that the machinery works, not that the
answers are good, and that is the right place to start.
**How to add:** keep a list of questions with what a good answer must contain, run
each through `agent.run`, and score the results. `patterns/evaluator.py` shows the
judging call.

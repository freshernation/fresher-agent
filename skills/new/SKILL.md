---
name: new
description: Create a new Fresher Agent project in a new folder. Use when the user wants to start building an AI agent from the Fresher Agent template.
argument-hint: "[folder-name]"
---

# Start a new Fresher Agent project

Create the project in the folder named by the user's argument: `$ARGUMENTS`.
If no name was given, use `my-agent`. If that folder already exists and is not
empty, stop and ask the user for another name.

1. Download the template:

   ```bash
   git clone --depth 1 https://github.com/freshernation/fresher-agent.git <folder>
   ```

2. Make it the user's own project. Inside `<folder>`, delete `.git`,
   `.claude-plugin` and the `skills` folder (they belong to the template's
   plugin, not to the user's agent), then run `git init`.

3. Run the setup script from inside `<folder>`:
   - Mac or Linux: `sh setup-fresher-agent.sh`
   - Windows: `setup-fresher-agent.bat`

4. Show the user the checklist the script printed. If any line says `[fail]`,
   fix that before going on.

5. Run the hello-world agent and show the output:

   ```bash
   .venv/bin/python run.py "How many words are in: the quick brown fox"
   ```

6. Tell the user, in three short lines: it is running on a fake model until they
   add a key to `.env`; tools live in `tools.py`; `README.md` is the one-page guide.

From here on, follow `AGENTS.md` in the new folder for any changes.

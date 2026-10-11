#!/bin/sh
# One-command setup for Mac and Linux:   sh setup-fresher-agent.sh
# Safe to run more than once.
set -e
cd "$(dirname "$0")"

PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 &&
        "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
        PYTHON="$candidate"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "Python 3.10 or newer is needed."
    echo "Install it from https://www.python.org/downloads/ and run this script again."
    exit 1
fi

echo "1/4  Creating .venv (a private folder for this project's packages)"
[ -d .venv ] || "$PYTHON" -m venv .venv

echo "2/4  Installing packages"
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt

echo "3/4  Creating .env"
[ -f .env ] || cp .env.example .env

echo "4/4  Checking that everything works"
echo
.venv/bin/python check.py

cat <<'EOF'

Next:
  source .venv/bin/activate          do this once in every new terminal
  python run.py                      chat with your agent
  open tools.py                      add your own tool
  open .env                          add an API key to use a real model
EOF

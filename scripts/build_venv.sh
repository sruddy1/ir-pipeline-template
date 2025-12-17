#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="$(basename "$PWD")"

python -m venv .venv
source .venv/Scripts/activate

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

python -m pip install -e .

python -m ipykernel install --user --name="$REPO_NAME"

#!/usr/bin/env bash
set -e
PYTHON=${PYTHON:-python3.12}
echo "Creating venv..."
$PYTHON -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "Done. Run: ./start.sh"

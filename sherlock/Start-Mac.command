#!/bin/bash
set -e
cd -- "$(dirname -- "$0")"
if [ ! -x .venv/bin/python ]; then
  python3.12 setup.py
fi
.venv/bin/python run.py "$@"
read -r -p "Press Enter to close..."

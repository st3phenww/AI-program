#!/usr/bin/env python3
"""Install a private environment without changing global Python packages."""
import os
import subprocess
import sys
import venv
from pathlib import Path

base = Path(__file__).resolve().parent
if sys.version_info[:2] != (3, 12):
    raise SystemExit("This package was tested with Python 3.12. Please install Python 3.12 first.")
env = base / ".venv"
python = env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
if not python.exists():
    venv.EnvBuilder(with_pip=True).create(env)
subprocess.run([str(python), "-m", "pip", "install", "--requirement", str(base / "requirements-lock.txt")], check=True)
subprocess.run([str(python), "-m", "pip", "check"], check=True)
subprocess.run([str(python), "-m", "sherlock_project", "--version"], check=True)
print("Ready. Run the Start-Windows.cmd or Start-Mac.command launcher.")

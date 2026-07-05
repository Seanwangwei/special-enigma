#!/bin/bash
# Launch the Exam Email Automation app.
# Automatically fixes the macOS cocoa plugin if needed (~2 s, wheel cached).
set -e
cd "$(dirname "$0")"
source .venv/bin/activate
pip install --force-reinstall PySide6_Essentials --quiet --no-deps 2>/dev/null
python3 app.py

#!/bin/bash
# Build the Exam Email Automation executable using PyInstaller.
# For macOS development — produces a bundle without Outlook support (pywin32 is Windows-only).
# SMTP delivery will work. Outlook delivery will error gracefully.
set -e
cd "$(dirname "$0")/.."

echo "=== Installing PyInstaller ==="
pip install pyinstaller --quiet

echo "=== Building ExamEmailAutomation ==="
pyinstaller ExamEmailAutomation.spec --clean --noconfirm

echo ""
echo "=== Build complete ==="
echo "Output: dist/ExamEmailAutomation/"
echo "Launch: dist/ExamEmailAutomation/ExamEmailAutomation"

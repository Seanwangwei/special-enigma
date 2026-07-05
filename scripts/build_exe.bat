@echo off
REM Build the Exam Email Automation executable using PyInstaller.
REM Run this on Windows to produce the release build.
cd /d "%~dp0\.."

echo === Installing PyInstaller ===
pip install pyinstaller --quiet

echo === Building ExamEmailAutomation ===
pyinstaller ExamEmailAutomation.spec --clean --noconfirm

echo.
echo === Build complete ===
echo Output: dist\ExamEmailAutomation\
echo Launch: dist\ExamEmailAutomation\ExamEmailAutomation.exe

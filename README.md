# Exam Result Email Automation

A Windows desktop application for Registrar Office staff that automatically generates and sends personalized exam result emails from a spreadsheet.

## Features

- Loads `.xlsx` spreadsheets exported from the Student Information System
- Groups rows by student ID and sends one email per student
- Supports multiple email templates
- Renders HTML email previews with a module result table
- Sends emails through Microsoft Outlook desktop
- Saves audit logs to `logs/send_log.xlsx`
- Maintains responsive GUI during bulk send operations

## Requirements

- Python 3.12+
- Windows for Outlook email sending
- Microsoft Outlook desktop client
- The following Python libraries:
  - PySide6
  - pandas
  - openpyxl
  - Jinja2
  - PyYAML
  - pywin32 (Windows only)

## Installation

1. Clone the repository.
2. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Run the application:

```bash
python3 app.py
```

## Configuration

Edit `config.yaml` to change locations for previews, logs, attachments, and templates.

Example:

```yaml
preview_folder: preview
log_folder: logs
attachment_folder: attachments
templates_folder: templates
use_default_outlook: true
```

## Folder Structure

- `app.py` — application entry point
- `config.yaml` — runtime folder configuration
- `requirements.txt` — Python dependency list
- `src/exam_email_automation/` — application package
  - `config/` — configuration loader
  - `excel/` — Excel parsing and student grouping
  - `email/` — email composition and Outlook delivery
  - `gui/` — PySide6 desktop interface
  - `logging/` — application and audit logging
  - `models/` — domain data classes
  - `services/` — preview and send workflows
  - `templates/` — HTML message templates
- `tests/` — automated unit tests

## Running the Application

1. Launch the app.
2. Browse and select the Excel file.
3. Preview generated emails.
4. Send a test email to verify formatting.
5. Send all emails.
6. Review the log output.

## Packaging for Windows

### Prerequisites (on a Windows machine)

- Python 3.12+
- [Inno Setup 6+](https://jrsoftware.org/isinfo.php) (install at default path)
- Microsoft Outlook (for Outlook integration testing)

### One-command build

```batch
scripts\build_installer.bat
```

This produces:
- `dist/ExamEmailAutomation/` — standalone application folder (no Python required)
- `dist/installer/ExamEmailAutomation-Setup-v1.0.0.exe` — installer for end users

### Manual build (step by step)

```batch
# 1. Install build dependencies
pip install -r requirements-dev.txt

# 2. Generate icon assets (if not already committed)
python scripts/generate_icon.py

# 3. Build executable with PyInstaller
pyinstaller ExamEmailAutomation.spec --clean --noconfirm

# 4. Build installer with Inno Setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\ExamEmailAutomation.iss
```

### macOS development build

On macOS, you can verify the PyInstaller build (SMTP delivery only, no Outlook):

```bash
./scripts/build_exe.sh
dist/ExamEmailAutomation/ExamEmailAutomation
```

## Testing

Run unit tests with:

```bash
python3 -m pytest -q
```

## Troubleshooting

- If the GUI does not launch, verify that `PySide6` is installed.
- If Outlook sending fails, confirm Outlook is installed and signed in.
- If the spreadsheet fails to load, check that required columns exist.
- If a template is missing, confirm the HTML file exists in `src/exam_email_automation/templates/`.

## FAQ

**Q: Does this require a Python install on the user machine?**
A: No. Run the installer (`Setup.exe`) and the app is ready to use. Python, Qt, and all dependencies are bundled.

**Q: Can I send attachments?**
A: Yes, select one attachment file through the Attachments picker in the GUI.

**Q: What happens if one email fails?**
A: The app continues processing the remaining emails and logs the failure.

## Developer Guide

- Business logic is separated from the GUI.
- Use `src/exam_email_automation/excel/excel_reader.py` to modify Excel parsing.
- Use `src/exam_email_automation/templates/template_engine.py` to update email rendering.
- Use `src/exam_email_automation/gui/main_window.py` for the desktop workflow.
- Add tests under `tests/` for new logic.

## Definition of Done

The project is complete when:

- The application launches as a Windows desktop GUI.
- A user can select an Excel file through the interface.
- The application validates required input and shows clear error messages.
- HTML previews are generated for every student and can be reviewed.
- A test email can be sent to verify formatting.
- One personalized email is sent per student using the correct template.
- A progress indicator remains responsive during sending.
- A detailed audit log is saved for every email attempt.
- The application can be packaged into a single executable for Windows without requiring Python installed.

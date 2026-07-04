# Project Overview

# Exam Result Email Automation

## What It Does

Exam Result Email Automation is a Windows desktop application that automates the preparation and delivery of personalized examination result emails to university students.

Registrar Office staff import an Excel spreadsheet exported from the Student Information System (SIS), review automatically generated HTML emails, and deliver them through Microsoft Outlook or SMTP — all through a simple graphical interface.

## Who Uses It

**Primary users:** University Registrar Office staff responsible for exam administration, student progression, and official communications.

**Secondary users:** IT administrators who deploy, configure, and support the application.

## Core Workflow

```
Import Excel  →  Validate  →  Preview Emails  →  Choose Delivery Method & Mode  →  Confirm  →  Send  →  Review Results  →  Audit Log Saved
```

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12+ |
| GUI | PySide6 (Qt6) |
| Excel | pandas + openpyxl |
| Email Templates | Jinja2 |
| Config | PyYAML |
| Outlook | pywin32 (COM) |
| SMTP | smtplib (stdlib) |
| Packaging | PyInstaller |
| Testing | pytest |

## Project Structure

```
exam-email-automation/
├── app.py                          # Application entry point
├── config.yaml                     # Runtime configuration
├── requirements.txt                # Python dependencies
├── ExamEmailAutomation.spec        # PyInstaller packaging spec
├── README.md                       # Quick-start guide
├── docs/
│   ├── PRD.md                      # Product Requirements Document
│   ├── Sprint_Roadmap.md           # Sprint plan and progress
│   ├── Project_Overview.md         # This file
│   └── Architecture.md             # Technical architecture
├── src/exam_email_automation/
│   ├── config/                     # YAML config loader
│   ├── email/                      # Email composition & delivery
│   ├── excel/                      # Excel parsing & student grouping
│   ├── gui/                        # PySide6 desktop interface
│   ├── logging/                    # App logging & audit log
│   ├── models/                     # Student & ModuleResult dataclasses
│   ├── services/                   # Preview & send workflows
│   ├── templates/                  # Jinja2 HTML email templates
│   └── validation/                 # Data validation
└── tests/                          # Automated unit tests
```

## How to Run (Development)

```bash
# Install dependencies
python3 -m pip install -r requirements.txt

# Run the application
python3 app.py

# Run tests
python3 -m pytest -q
```

## How to Build (Windows Packaging)

On a Windows machine with PyInstaller:

```bash
pyinstaller ExamEmailAutomation.spec
```

The output is placed in the `dist/` directory.

## Key Design Decisions

1. **Layered architecture** — GUI → Services → Business Logic → Models. Each layer is independently testable.
2. **Outlook-first delivery** — University Registrar Offices use centrally managed Outlook. SMTP is available as a fallback.
3. **Draft-by-default** — The recommended workflow is Preview → Outlook Draft → Manual Review → Send to prevent accidental mass email delivery.
4. **One email per student** — The Excel reader groups all module rows by Student ID, ensuring each student receives exactly one notification.
5. **Audit everything** — Every email attempt is logged with timestamp, recipient, template, and status in a timestamped Excel file.

## External Dependencies

- **Microsoft Outlook Desktop** (2016 or later) — for email delivery via Outlook
- **Excel files from SIS** — the spreadsheet must contain the columns listed in `PRD.md` Section FR-1

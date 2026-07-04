# Sprint Roadmap

# Exam Result Email Automation

Version: 0.4.0 (Production Ready)

Last Updated: July 2026

---

# Project Goal

Build a Windows desktop application that enables university Registrar Office staff to efficiently generate, review, and deliver personalized examination result emails to students directly from an Excel spreadsheet.

The application should reduce manual administrative work, minimize human error, provide a complete audit trail, and be simple enough for non-technical administrative staff to operate.

---

# Development Philosophy

Development follows an incremental sprint-based approach.

Each sprint delivers a complete and testable increment while maintaining production-quality code, automated tests, and clear separation of responsibilities.

---

# Sprint 1 — Core Backend Foundation

Status: ✅ Completed

Objective

Build the core business logic required to process examination data independently of any user interface.

Major Deliverables

- Project structure established
- Configuration system
- Domain models
- Excel parser
- Student grouping by Student ID
- Email template engine (Jinja2)
- HTML email generation
- Validation framework
- Audit logging framework
- Preview generation service
- Initial unit tests

Architecture Introduced

GUI
↓

Services
↓

Business Logic
↓

Models

Outcome

The application was capable of reading examination data and generating personalized email content programmatically.

No graphical user interface or email delivery workflow existed at this stage.

---

# Sprint 2 — Email Delivery & Business Workflow

Status: ✅ Completed

Objective

Implement production email delivery capabilities while keeping delivery methods flexible and safe.

Major Deliverables

- Microsoft Outlook integration
- SMTP delivery implementation
- Delivery service abstraction
- Preview mode
- Delivery mode architecture
- Audit log export
- Email attachment support
- Configuration enhancements
- Additional automated tests

Key Design Decisions

### Outlook is the primary delivery mechanism

Because university Registrar Offices typically communicate using a centrally managed Outlook environment.

### Delivery Modes

Three delivery modes were introduced:

- Preview Only
- Create Outlook Drafts
- Send Immediately

The recommended operational workflow is:

Preview → Outlook Draft → Manual Review → Send

This minimizes the risk of accidental mass email delivery.

Outcome

The application became capable of producing production-ready email messages and delivering them through Outlook or SMTP.

---

# Sprint 3 — Desktop User Interface (MVP)

Status: ✅ Completed

Objective

Provide a desktop application that can be operated by Registrar Office staff without requiring technical knowledge.

Major Deliverables

- PySide6 desktop application
- Main application window
- Excel file picker
- Email preview dialog
- Validation dialog
- Delivery method selection dialog
- Confirmation dialog
- Progress dialog
- Results summary dialog
- Background worker for long-running operations
- GUI responsiveness during processing
- End-to-end application workflow

Typical User Workflow

Launch Application

↓

Select Excel Spreadsheet

↓

Validate Input

↓

Preview Emails

↓

Choose Delivery Method

↓

Confirm Operation

↓

Generate Drafts / Send Emails

↓

View Results Summary

↓

Audit Log Saved

Outcome

The project reached Minimum Viable Product (MVP) status.

The application now provides a complete end-to-end workflow from spreadsheet import to email delivery.

---

# Current Project Status

Overall Status

🟢 Production Ready

Completed

✅ Backend architecture

✅ GUI with full wizard workflow

✅ Validation (columns, emails, pre-send checks)

✅ Email template engine (3 templates)

✅ Outlook integration with shared mailbox support

✅ SMTP implementation (fully wired)

✅ Delivery modes (Preview/Draft/Send)

✅ Preview generation (background thread)

✅ Audit logging (timestamped)

✅ Automated tests (27 tests)

✅ Documentation (PRD, Sprint Roadmap, Project Overview, Architecture)

Repository Status

Branch: main

Working Tree: Sprint 4 changes pending commit

Latest Milestone

Sprint 4 completed. v0.4.0 Production Ready.

---

# Sprint 4 — Production Readiness

Status: ✅ Completed

Objective

Prepare the application for real-world deployment within a university Registrar Office.

Completed Deliverables

## Launch & Configuration

- ✅ Fixed `app.py` crash (Config not passed to MainWindow)
- ✅ Fixed template folder resolution with dev/production fallback
- ✅ Config-driven provider selection (Outlook/SMTP)

## Wizard Workflow

- ✅ Full dialog chain wired into MainWindow: Validate → Delivery Method → Mode → Confirm → Send → Results
- ✅ `ValidationResultsDialog` integrated with pre-send validation
- ✅ `DeliveryMethodDialog` with Outlook/SMTP + mailbox selection
- ✅ `DeliveryModeDialog` with Preview/Draft/Send options
- ✅ `ConfirmationDialog` with summary stats before execution
- ✅ `ResultsDialog` with tabbed results and clipboard copy

## Provider & Integration

- ✅ SMTPEmailSender wired into SendService (provider dispatch)
- ✅ Shared mailbox support fixed (`_get_target_account()` now sets `SendUsingAccount`)
- ✅ Config `delivery_mode` properly parsed and applied at runtime

## Data Integrity

- ✅ NaN guard in ExcelReader (`_safe_str()` helper)
- ✅ Timestamped audit log filenames (`send_log_{timestamp}.xlsx`)
- ✅ Pre-send validation (missing emails, duplicate IDs)

## UI & UX

- ✅ Multi-file attachment support (was single-file)
- ✅ Dynamic template status from actual files on disk
- ✅ HTML generation deferred to background thread (PreviewWorker)
- ✅ SectionLabel widget used for headers
- ✅ ResultsDialog clipboard closure bug fixed

## Documentation

- ✅ `docs/Project_Overview.md` created
- ✅ `docs/Architecture.md` created
- ✅ `docs/PRD.md` created (Sprint 3)

## Testing

- ✅ All 27 tests pass (23 existing + 4 new)
- ✅ NaN guard test, SMTP provider test, template path tests added

Success Criteria

A Registrar Office staff member with no technical background can install, operate, and complete an entire examination notification cycle without developer assistance. ✅

---

# Future Roadmap

## Phase 2

Potential Enhancements

- Microsoft Graph integration
- Exchange Online support
- Multiple attachment handling
- Email scheduling
- Rich progress reporting
- Multi-language templates
- Template editor

---

## Phase 3

Enterprise Features

- User authentication
- Role-based permissions
- Central configuration management
- Database-backed audit logs
- Reporting dashboard
- Batch history
- Email analytics

---

# Definition of MVP

The MVP is considered complete when the application can:

✓ Import an Excel spreadsheet

✓ Validate required data

✓ Group records by student

✓ Select the correct email template

✓ Generate personalized HTML emails

✓ Allow staff to preview emails

✓ Create Outlook drafts or send emails

✓ Record every operation in an audit log

✓ Remain responsive during bulk processing

✓ Package as a Windows desktop application

---

# Notes for Future Developers and AI Assistants

Before implementing new functionality:

1. Read README.md.
2. Read Project_Overview.md.
3. Read Architecture.md.
4. Review this Sprint Roadmap.
5. Inspect the current repository.
6. Preserve the existing architecture unless a documented design change is approved.
7. Maintain automated test coverage.
8. Keep Outlook as the primary enterprise integration unless project requirements change.

Sprint numbers represent historical milestones.

Future development should continue from Sprint 4 rather than modifying the goals of completed sprints.

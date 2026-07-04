# Sprint Roadmap

# Exam Result Email Automation

Version: 0.3.0 (Current MVP)

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

🟢 MVP Complete

Completed

✅ Backend architecture

✅ GUI

✅ Validation

✅ Email template engine

✅ Outlook integration

✅ SMTP implementation

✅ Delivery modes

✅ Preview generation

✅ Audit logging

✅ Automated tests

Repository Status

Branch: main

Working Tree: Clean

Latest Milestone

Sprint 3 completed.

---

# Sprint 4 — Production Readiness

Status: 📋 Planned

Objective

Prepare the application for real-world deployment within a university Registrar Office.

Planned Deliverables

## User Experience

- GUI polish
- Improved icons and branding
- Better validation messages
- Keyboard shortcuts
- Improved accessibility

## Outlook Integration

- Shared mailbox support
- Explicit Outlook account selection
- Better Outlook error handling

## Reliability

- Retry failed emails
- Resume interrupted sending
- Duplicate email prevention
- Improved exception handling

## Deployment

- Windows installer
- Code signing (optional)
- Configuration wizard
- Auto-update strategy (future consideration)

## Documentation

- End User Guide
- Administrator Guide
- Deployment Guide
- Troubleshooting Guide

## Testing

- End-to-end testing
- Large dataset performance testing
- Windows compatibility verification
- User Acceptance Testing (UAT)

Success Criteria

A Registrar Office staff member with no technical background can install, operate, and complete an entire examination notification cycle without developer assistance.

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

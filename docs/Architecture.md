# Architecture

# Exam Result Email Automation

## Layer Diagram

```
┌──────────────────────────────────────────────┐
│  GUI (PySide6)                               │  Presentation
│  main_window.py, dialogs, widgets             │
├──────────────────────────────────────────────┤
│  Services                                    │  Orchestration
│  PreviewService, SendService                  │
├──────────────────────────────────────────────┤
│  Business Logic                              │  Domain
│  ExcelReader, EmailBuilder, TemplateEngine,   │
│  Validator, OutlookEmailSender,               │
│  SMTPEmailSender                              │
├──────────────────────────────────────────────┤
│  Models                                      │  Data
│  Student, ModuleResult, Config,               │
│  EmailMessage, DeliveryMode                   │
└──────────────────────────────────────────────┘
```

## Module Design

### `config/` — Configuration

- `Config` is a frozen dataclass holding all runtime settings.
- `ConfigLoader` reads `config.yaml`, resolves relative folder paths to absolute, and provides sensible defaults when the file is missing.
- The config supports both Outlook and SMTP delivery paths.

### `excel/` — Excel Parsing

- `ExcelReader.load_students()` reads a `.xlsx` file via pandas, validates required columns, normalizes headers (case-insensitive, whitespace-tolerant), groups rows by Student ID, and returns a list of `Student` objects.
- `_safe_str()` guards against NaN values from empty cells, preventing literal `"nan"` strings in student data.
- Each student gets one `Student` object with a list of `ModuleResult` objects for their individual module rows.

### `email/` — Email Composition & Delivery

- `DeliveryMode` enum: `PREVIEW_ONLY`, `CREATE_DRAFTS`, `SEND_IMMEDIATELY`.
- `EmailBuilder` composes an `EmailMessage` from a `Student` and rendered HTML. It maps template names to subject lines via a lookup table.
- `OutlookEmailSender` uses `win32com.client` (COM) to automate Microsoft Outlook. Supports shared mailbox selection via `SendUsingAccount`. Exposes `create_draft()` and `send_message()`.
- `SMTPEmailSender` uses `smtplib` with SSL/TLS support. Takes an `SMTPConfig` and an `EmailMessage`, builds a MIME multipart message, and sends it. Used for cross-platform delivery and testing.

### `gui/` — Desktop Interface

- `MainWindow` (QMainWindow) is the primary window with groups for file selection, attachments, actions, progress, and logging.
- `PreviewDialog` shows a two-pane view: student list + rendered HTML.
- `ValidationResultsDialog` shows pre-send validation errors (missing emails, duplicate IDs) with abort/continue options.
- `DeliveryMethodDialog` lets the user choose Outlook vs SMTP and select a mailbox.
- `DeliveryModeDialog` lets the user choose Preview Only, Create Drafts, or Send Immediately.
- `ConfirmationDialog` shows a summary before execution.
- `ResultsDialog` displays post-send results with tabs for all records and errors, plus clipboard copy.
- `SectionLabel` is a reusable styled header widget.

**Threading model:**
- `SendWorker(QThread)` sends emails in the background, emitting progress and status signals.
- `PreviewWorker(QThread)` generates HTML previews off the main thread after Excel loading.
- The main thread handles all UI updates via signal/slot connections.

### `logging/` — Application & Audit Logging

- `configure_logging()` sets up a standard Python logger with console and file (`application.log`) handlers.
- `AuditLogger.save()` writes a timestamped `send_log_{timestamp}.xlsx` file containing every email attempt with: Time, Student ID, Email, Template, Status, Error.

### `models/` — Domain Data Classes

- `Student` (dataclass): `student_id`, `first_name`, `surname`, `email`, `template_name`, `stage_average`, `pass_credits`, `failed_modules`, `modules`. Exposes `full_name` property and `to_context()` for Jinja2 rendering.
- `ModuleResult` (frozen dataclass): `module_code`, `module_name`, `assessment_format`, `attempt`, `pass_credits`.

### `services/` — Workflow Orchestration

- `PreviewService` renders HTML via `TemplateEngine` and optionally saves preview files to disk.
- `SendService` orchestrates per-student email processing based on delivery mode and provider. It validates email addresses, composes messages, dispatches to the appropriate sender (Outlook or SMTP), and records results. Supports runtime provider and mode selection.

### `templates/` — HTML Templates

- `TemplateEngine` wraps Jinja2 with a `FileSystemLoader`. Templates are resolved by name from the `Email Template` column in the spreadsheet.
- Three templates are bundled: `template1.html` (progression), `template2.html` (reassessment), `template3.html` (extenuating circumstances).
- `generate_module_table()` builds an HTML `<table>` of module results for insertion into templates.

### `validation/` — Data Validation

- `Validator` provides: column validation (required headers), email format validation (regex), and file existence checks.
- The `MainWindow._validate_loaded_data()` method performs batch validation on loaded students before sending.

## Data Flow

```
Excel File (.xlsx)
  ↓ ExcelReader.load_students()
[Student] objects
  ↓ PreviewWorker (background thread)
  ↓ TemplateEngine.render(student)
HTML map {student_id: html_body}
  ↓ User wizard (Validate → Method → Mode → Confirm)
  ↓ SendWorker (background thread)
  ↓ SendService.send_student()
  ↓ OutlookEmailSender or SMTPEmailSender
Email delivered + Audit Log saved
```

## Threading Model

```
Main Thread (GUI)
  ├─ PreviewWorker (QThread) — HTML generation after Excel load
  └─ SendWorker (QThread) — Email sending/drafting
```

- Workers emit signals (`progress_changed`, `status_message`, `finished`) that the main thread connects to via Qt's signal/slot mechanism.
- The GUI never blocks; progress bars and log output update in real time during bulk operations.

## Error Handling Strategy

- **Per-student failure isolation:** If one email fails, the batch continues. The error is recorded in the audit log.
- **Validation-first:** Data is validated before any email is sent. Users can abort if validation errors are found.
- **Graceful degradation:** If configured template path doesn't exist, the app falls back to the source package directory.
- **Configurable provider:** Falls back to SMTP when Outlook is unavailable (cross-platform development).

## Configuration Contract

See `config.yaml` for the full schema. Key fields:

| Field | Type | Default | Description |
|---|---|---|---|
| `preview_folder` | path | `preview` | HTML preview output directory |
| `log_folder` | path | `logs` | Application and audit log directory |
| `templates_folder` | path | (see config) | Jinja2 template directory |
| `delivery_mode` | string | `create_drafts` | `preview_only`, `create_drafts`, or `send_immediately` |
| `email_provider` | string | `outlook` | `outlook` or `smtp` |
| `outlook_mailbox_email` | string | null | Shared mailbox email (Outlook only) |
| `smtp_*` | various | — | SMTP host, port, credentials, TLS/SSL flags |

## Test Strategy

- **Backend unit tests:** All business logic modules have pytest coverage (`tests/` directory).
- **Mocking:** Outlook COM calls are mocked; SMTP uses `aiosmtpd` for local integration testing.
- **No GUI tests in CI:** Qt-based GUI tests require a display and are run manually on Windows.
- **Test configuration:** `pytest.ini` sets `pythonpath = src` for clean imports.

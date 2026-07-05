# Sprint Roadmap

# Exam Result Email Automation

Version: 1.0.0 (Sprint 8 Complete — Production Packaging & Distribution)

Last Updated: July 5, 2026

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

# Sprint 5 — Dynamic Template Upload & Variable Detection

Status: ✅ Completed

Objective

Replace hardcoded Excel column names and templates with a dynamic, template-first workflow where Registrar staff upload their own Word (.docx) email templates.

Completed Deliverables

## DOCX Template Support

- ✅ Word (.docx) template upload with {{variable}} placeholders
- ✅ Variable extraction from .docx paragraphs and tables
- ✅ DOCX-to-HTML conversion preserving bold/italic formatting
- ✅ Variable classification (simple vs. special like module_table)
- ✅ Companion YAML support for template subject lines
- ✅ GUI prompt for subject line when no YAML found

## Dynamic Validation

- ✅ Dynamic column validation driven by template variables
- ✅ MismatchReport — shows missing and unused columns
- ✅ User alert dialog with Continue/Cancel on mismatch
- ✅ Special variables (module_table) excluded from Excel validation
- ✅ Backward compatible with bundled HTML templates

## Model Flexibility

- ✅ Student.extra_fields dict for arbitrary Excel columns
- ✅ to_context() merges structured fields + extra fields
- ✅ ExcelReader captures unknown columns automatically

## Template Engine Updates

- ✅ ChoiceLoader (DictLoader + FileSystemLoader) for uploaded + bundled templates
- ✅ EmailBuilder.override_subject for DOCX template subject lines
- ✅ Template clear/revert to bundled HTML templates

## Testing

- ✅ 55 tests pass (27 existing + 17 docx parser + 11 integration)
- ✅ Integration tests: parse → validate → render → send pipeline

---

# Sprint 6 — UI/UX Design System Implementation & Design QA

Status: 📋 Planned

Objective

Implement the complete design system from `docs/design-mockup.html` and verify every screen matches the design specification through structured design review with side-by-side screenshot comparison.

Design Source: `docs/design-mockup.html` (committed at 8031f82)

---

## Phase 1 — Design Token Infrastructure

### 1.1 Create Theme Module

File: `src/exam_email_automation/gui/theme.py`

Define all design tokens as Python constants:
- Color palette (12 colors: primary, success, warning, error, neutral scale)
- Typography scale (5 sizes: xs/11px → 2xl/24px)
- Spacing scale (8 steps: 4px → 32px)
- Border radius scale (4 steps: 4px → 12px)
- Shadow definitions (not applicable to QSS, but document for reference)

```python
# Example structure
class Colors:
    PRIMARY = "#2563eb"
    PRIMARY_HOVER = "#1d4ed8"
    SUCCESS = "#16a34a"
    # ... etc

class Fonts:
    SANS = "Segoe UI, -apple-system, system-ui, sans-serif"
    MONO = "Consolas, SF Mono, Cascadia Code, monospace"
```

### 1.2 Create App-Wide QSS Stylesheet

File: `src/exam_email_automation/gui/styles.qss`

Translate design tokens into QSS:
- Global font family and default colors
- QGroupBox → card style (white background, border, rounded corners)
- QPushButton variants (primary, secondary, ghost, danger, success)
- QLineEdit (normal, readonly, focus with blue glow)
- QTextEdit / QTextBrowser (log area dark theme)
- QProgressBar (rounded track, blue fill)
- QLabel badges (via dynamic property selectors)
- QRadioButton → card-style radio options
- QTabWidget / QTabBar (tab styling)
- QListWidget (preview student list)
- QComboBox (dropdown)
- Scrollbar styling
- QStatusBar

### 1.3 Apply Stylesheet at Startup

Update `app.py`:
- Load `styles.qss` from file
- Apply via `app.setStyleSheet(qss_content)`
- Set `QApplication.setOrganizationName("ExamEmailAutomation")` for QSettings
- Set `QApplication.setApplicationName("Exam Email Automation")`
- Set default font family

---

## Phase 2 — Component Implementation

### 2.1 Button Variants

Style all QPushButtons with semantic classes via `setProperty()` or object-name selectors:
- Primary: blue background, white text (Preview, Send, Continue)
- Secondary: white background, border (Browse, Copy to Clipboard)
- Ghost: transparent, gray text (Clear, Back, Cancel)
- Danger: red background (only when destructive)
- Success: green background (only when affirmative)

### 2.2 Badge Widget

Create a reusable badge system:
- Option A: `QLabel` subclass with dynamic property `data-badge="success|warning|error|info"`
- Option B: Plain `QLabel` with inline stylesheet for each instance
- Decision: Option A for reusability

Use cases:
- Template vars detected count
- Student count in Excel card
- Pass/Fail/EC counts
- Status indicators in results

### 2.3 Step Indicator Widget

Create a wizard progress widget showing current step:
- Reusable across Method/Mode/Confirm dialogs
- Shows: Validate → Method → Mode → Confirm → Results
- Active step: blue filled circle
- Done step: green checkmark circle
- Future step: gray outlined circle
- Connector lines between steps

### 2.4 Radio Option Cards

Style QRadioButton as card-style selectable options:
- Border on all sides, rounded corners
- Selected state: blue border + light blue background
- Hover: light gray background
- Title + description text (use `\n` properly or separate labels)

### 2.5 Log Panel Dark Theme

Style the log QTextEdit:
- Dark background (#0f172a)
- Light monospace text (#e2e8f0)
- Color-coded lines: green for success, red for errors
- Timestamp in muted gray

---

## Phase 3 — Screen-by-Screen Implementation

### 3.1 Main Window — Empty State

Match mockup:
- [ ] Remove hardcoded Courier font from ConfirmationDialog → use theme
- [ ] Section cards with uppercase header labels + icons (use Unicode)
- [ ] Browse/Clear button groups consistent across all three file sections
- [ ] Actions section: buttons disabled until data loaded
- [ ] Progress and Log sections hidden on startup, shown when active
- [ ] Status bar: green dot + "Ready" message
- [ ] Set minimum size 480×400, default 680×680
- [ ] Window icon set (generate simple SVG icon or use Qt built-in)

### 3.2 Main Window — Loaded State

Match mockup:
- [ ] Template card: shows filename + variable badges + Clear button
- [ ] Excel card: shows filename + student count badge + Clear button
- [ ] Variable badges displayed as wrap-row of small blue pills
- [ ] Actions all enabled
- [ ] Progress bar visible with percentage + "N / M" label
- [ ] Log panel visible with timestamped, color-coded entries

### 3.3 Preview Dialog

Match mockup:
- [ ] Split-pane layout: QListWidget (left, fixed width) + QTextBrowser (right, stretch)
- [ ] Active student highlighted in blue
- [ ] Email metadata header (To, Subject) above rendered HTML
- [ ] Close button right-aligned

### 3.4 Validation Results Dialog

Match mockup:
- [ ] Warning/error card at top (red background, red border)
- [ ] Summary: "N column mismatches detected"
- [ ] Details section with color-coded list (red = missing, amber = unused)
- [ ] Two action buttons: "Continue Anyway" (ghost) + "Go Back & Fix" (primary)

### 3.5 Delivery Method Dialog

Match mockup:
- [ ] Step indicator showing Step 1 active
- [ ] Radio card: Outlook (with description)
- [ ] Radio card: SMTP (with description)
- [ ] Outlook account section (dropdown + label) — disabled when SMTP selected
- [ ] Back (ghost, left) + Continue (primary, right)

### 3.6 Delivery Mode Dialog

Match mockup:
- [ ] Step indicator showing Step 2 active
- [ ] Three radio cards with emoji icons + titles + descriptions:
  - 🔍 Preview Only
  - 📝 Create Outlook Drafts (Default) — pre-selected
  - 📨 Send Immediately
- [ ] Back (ghost) + Continue (primary)

### 3.7 Confirmation Dialog

Match mockup:
- [ ] Step indicator showing Step 3 active
- [ ] Stats card: monospace, centered, with Unicode dividers
- [ ] Student count + Pass/Fail/EC breakdown with color coding
- [ ] Delivery info card (blue accent): Method + Mode
- [ ] Back (ghost) + "📨 Process N Emails" (primary, large)

### 3.8 Results Dialog

Match mockup:
- [ ] Success header: green circle checkmark + "Processing Complete" + sent/failed badges
- [ ] QTabWidget: "All Records" + "Errors (N)"
- [ ] Pipe-delimited log-style table in monospace font
- [ ] "Copy to Clipboard" (secondary) + "Close" (primary)
- [ ] Copy button shows "Copied!" feedback for 1.5s

---

## Phase 4 — UX Polish

### 4.1 Dialog Centering

- [ ] All dialogs center on parent window instead of hardcoded (200,200) positions
- [ ] Replace `setGeometry()` calls with `self.move(parent.x() + (parent.width() - self.width()) // 2, parent.y() + ...)` or use Qt's built-in centering

### 4.2 Keyboard Shortcuts

- [ ] Enter/Return activates primary button in dialogs
- [ ] Escape closes dialog (reject) — already works via Qt default
- [ ] Ctrl+O → Browse Excel (if main window focused)
- [ ] Ctrl+P → Preview Emails
- [ ] Alt+letter mnemonics on key buttons (via `&` in text)

### 4.3 Window Icon

- [ ] Generate a simple SVG application icon (or use a Unicode character)
- [ ] Set via `QApplication.setWindowIcon()`
- [ ] Also set on individual dialogs via `setWindowIcon()`

### 4.4 Loading States

- [ ] Preview generation shows busy cursor or progress indicator
- [ ] Send operation: progress bar updates in real-time
- [ ] Status bar message updates during operations

### 4.5 QSettings Persistence

- [ ] Save/restore main window size and position
- [ ] Save/restore last used directory for file dialogs
- [ ] QSettings initialized in `app.py` with org/app name

---

## Phase 5 — Design Review & QA

### 5.1 Screenshot Capture

For each of the 8 screens, capture screenshots showing:
1. **Empty/Main Window** — both empty and loaded states
2. **Preview Dialog** — with a student selected
3. **Validation Dialog** — with mismatches shown
4. **Delivery Method Dialog** — Outlook selected
5. **Delivery Mode Dialog** — Draft selected
6. **Confirmation Dialog** — with stats populated
7. **Results Dialog** — with sent + errors

### 5.2 Side-by-Side Comparison

Create a design conformance document at `docs/sprint6-design-review.html`:

For each screen:
- Left: design-mockup.html screenshot (reference)
- Right: actual app screenshot (implementation)
- Below: conformance checklist (colors, spacing, typography, layout)
- Status: ✅ Match / ⚠ Minor Diff / ❌ Does Not Match

### 5.3 Design Conformance Criteria

Each screen assessed on:
| Dimension | Check |
|-----------|-------|
| Colors | Do hex values match the design tokens? |
| Typography | Font sizes, weights, families match? |
| Spacing | Margins, padding, gaps match the 4px grid? |
| Layout | Widget order and alignment match? |
| States | Hover, focus, disabled, active states correct? |
| Responsiveness | Window resize behavior acceptable? |

### 5.4 Bug Remediation

- [ ] Log all design discrepancies to UAT Bug Log
- [ ] Fix each discrepancy
- [ ] Re-capture screenshots
- [ ] Re-compare until all screens pass

---

## Definition of Done for Sprint 6

- [ ] `theme.py` and `styles.qss` created and loaded at startup
- [ ] All 8 screens match their mockup counterparts
- [ ] Badge widget reusable across the app
- [ ] Step indicator widget shows correct wizard progress
- [ ] Radio option cards styled as per mockup
- [ ] Dark-themed log panel renders color-coded entries
- [ ] All dialogs centered on parent window
- [ ] Keyboard shortcuts functional (Enter/Esc minimum)
- [ ] Window icon applied
- [ ] QSettings persists window geometry
- [ ] Design review document created with side-by-side screenshots
- [ ] All discrepancies logged and fixed
- [ ] All 55 existing tests still pass
- [ ] No regressions in functionality

---

## Test Strategy for Sprint 6

### Automated

```bash
python3 -m pytest -q  # Must remain 55+ passing
```

### Manual Design QA

1. Launch app → compare main window (empty) against mockup
2. Upload .docx template → compare variable badges against mockup
3. Browse Excel → compare loaded state against mockup
4. Click Preview → compare Preview dialog against mockup
5. Trigger validation error → compare Validation dialog against mockup
6. Click Send All → step through Method → Mode → Confirm dialogs
7. Complete send → compare Results dialog against mockup
8. Screenshot each screen, paste into `docs/sprint6-design-review.html`
9. Mark conformance for each dimension

---

# Sprint 7 — Dynamic DOCX Table Population

Status: ✅ Completed

Objective

Enable DOCX email templates to contain custom tables whose rows are automatically populated from Excel module data per student, instead of requiring `{{module_table}}` with hardcoded columns.

Design Source: Real user scenario — Registrar Office templates contain bespoke module tables with office-specific columns.

---

## Phase 1 — Table Detection & Header Analysis

### 1.1 Detect Tables in DOCX

File: `docx_parser.py`

Extend `parse_and_convert()` to classify each table found in the DOCX:
- **Data table**: Has a first row with bold text (header row) + subsequent rows (empty or with placeholders).
- **Static table**: All rows are static content — leave as-is.

### 1.2 Extract Column Mapping

For each data table:
- Read header row cell text → normalize to match Excel columns / ModuleResult fields.
- Build a mapping: `{header_text: field_name}` for each column.
- Example: `"Module Code"` → `"module_code"`, `"Module Name"` → `"module_name"`, `"Credits"` → `"credits"`.

### 1.3 Identify Unmapped Columns

Table headers that don't match any Excel column are tracked as "unmapped". These cells will render empty in generated rows. No error — blank cells are allowed.

---

## Phase 2 — Dynamic Row Generation

### 2.1 Replace Empty Rows with Jinja2 Loop

Instead of converting empty table rows to static `<tr><td></td>...</tr>` HTML, generate a Jinja2 `{% for %}` block:

```html
{% for module in student.modules %}
<tr>
  <td>{{ module.module_code }}</td>
  <td>{{ module.module_name }}</td>
  <td>{{ module.get('credits', '') }}</td>
  ...
</tr>
{% endfor %}
```

### 2.2 Update ModuleResult Model

File: `models/module_result.py`

Add an `extra_fields` dict to `ModuleResult` (mirroring `Student.extra_fields`) so that any Excel column beyond the 5 known module fields is accessible in table row templates.

### 2.3 Update ExcelReader

File: `excel_reader.py`

When building `ModuleResult` objects, capture columns beyond the 5 known module columns into `ModuleResult.extra_fields` using the same all-rows dedup logic from BUG-007.

### 2.4 Enhance `generate_module_table()`

File: `template_engine.py`

`generate_module_table()` currently hardcodes 4 columns. Update to accept an optional `columns: list[str] | None` parameter. When provided, generates only those columns. When `None`, uses the default 4-column output.

---

## Phase 3 — Template Rendering Integration

### 3.1 Wire Table Detection into Template Engine

When `parse_and_convert()` detects a data table, store the column mapping in `TemplateInfo`. The `TemplateEngine.render()` method uses this mapping to pass the right columns to `generate_module_table()`.

### 3.2 Handle Mixed Templates

A single DOCX may have:
- Inline `{{variables}}` in paragraphs → existing behaviour
- A data table → dynamic rows
- Static tables (no header row detected) → existing behaviour

All three must coexist in one template.

---

## Phase 4 — Testing & Verification

### 4.1 Unit Tests

- DOCX table header detection (bold row → header)
- Column name normalization and matching
- Empty DOCX tables (no data rows)
- Tables with no matching Excel columns
- Multiple tables in one DOCX
- Mixed inline variables + data tables

### 4.2 Integration Tests

- Full pipeline: .docx with table → parse → Excel load → render → verify HTML contains correct number of data rows
- Student with 0 modules (edge case — table should show "No module results")
- Student with 5 modules (many rows)

### 4.3 Backward Compatibility

- Existing `{{module_table}}` templates unchanged
- Existing non-table DOCX templates unchanged
- All 120 existing tests must still pass

---

## Definition of Done for Sprint 7

- [ ] DOCX tables with bold header rows are detected as data tables
- [ ] Column mapping built from header text → Excel fields
- [ ] Empty table rows replaced with Jinja2 `{% for %}` loop
- [ ] `ModuleResult.extra_fields` captures non-standard module columns
- [ ] `generate_module_table()` accepts optional column list
- [ ] Data rows populated per student module count (Wang Wei = 2 rows)
- [ ] Unmapped columns render as empty cells (no error)
- [ ] Static tables (no header) left unchanged
- [ ] `{{module_table}}` special variable still works
- [ ] All 120+ existing tests pass
- [ ] New tests cover table detection, column mapping, row generation
- [ ] UAT verified with `test with table.docx` + `test.xlsx`

---

## Test Strategy for Sprint 7

### Automated

```bash
python3 -m pytest -q  # Must remain 120+ passing + new table tests
```

### Manual UAT

1. Upload `test with table.docx` → verify table detected, columns mapped
2. Load `test.xlsx` → verify Wang Wei shows 2 table rows
3. Preview email → verify table populated correctly
4. Verify inline `{{variables}}` still work alongside table
5. Verify existing non-table templates still work

---

# Sprint 8 — Production Packaging & Distribution

Status: ✅ Completed

## Sprint Goal

Transform the application from a developer project into an installable Windows desktop application that can be used by Registrar Office staff without requiring any technical knowledge.

---

## User Story

As a Registrar Office staff member,

I want to download a single installer,

so that I can install and launch the application like any other Windows software without needing Python, GitHub, or developer tools.

---

## Business Value

Current experience:

```
GitHub
→ Clone Repository
→ Install Python
→ Install Dependencies
→ Run app.py
```

Target experience:

```
Download Setup.exe
→ Double-click Install
→ Desktop Shortcut Created
→ Double-click Icon
→ Application Launches
```

This significantly lowers the barrier to adoption and enables deployment to non-technical users.

---

## Technical Solution

### Application Packaging

Use **PyInstaller** to package the Python application into a standalone executable.

Deliverables:

- `ExamEmailAutomation.exe`
- Bundled Python Runtime
- Bundled Qt Libraries
- Bundled Templates
- Bundled Configuration
- No Python installation required

---

### Windows Installer

Use **Inno Setup** to create a professional Windows installer.

Installer responsibilities:

- Install application
- Create Desktop Shortcut
- Create Start Menu Shortcut
- Create Uninstaller
- Install required runtime libraries (if needed)
- Configure application folders

Output:

`ExamEmailAutomation-Setup.exe`

---

### Application Metadata

Configure:

- Application Name
- Version Number
- Publisher
- Application Icon
- Product Description

---

### First Launch Experience

On first launch automatically create:

```
preview/
logs/
attachments/
```

Load default configuration if none exists.

---

### Application Icon

Create:

- Desktop icon
- Start Menu icon
- Taskbar icon
- Window icon

---

### Versioning

Adopt Semantic Versioning.

Examples:

- `v1.0.0`
- `v1.1.0`
- `v2.0.0`

Display version inside:

```
Help → About
```

---

## Acceptance Criteria

- [ ] Application installs using Setup.exe *(Windows QA — W2, W3)*
- [ ] No Python installation required *(Windows QA — W7)*
- [ ] Desktop shortcut created *(Windows QA — W4)*
- [ ] Application launches successfully *(macOS QA — M9)*
- [ ] Preview, Logs, and Attachment folders created automatically
- [ ] Uninstaller available in Windows *(Windows QA — W5, W16)*
- [ ] Application icon displayed correctly *(Windows QA — W15)*
- [ ] Version information visible *(macOS QA — M3, M4)*

> **Note:** All code complete. macOS QA 11/18 pass. Windows QA requires a Windows machine.

---

## Deliverables

- ✅ Standalone EXE — PyInstaller spec (`ExamEmailAutomation.spec`) + build scripts
- ✅ Windows Installer — Inno Setup script (`installer/ExamEmailAutomation.iss`) + build script
- ✅ Application Icon — `resources/icon.ico` (multi-res), `resources/icon.png` (256px)
- ✅ Version Metadata — `__version__ = "1.0.0"` + `version.py`
- ✅ Installation Guide — README "Packaging for Windows" section

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

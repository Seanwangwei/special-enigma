# UAT Bug Tracking Log

# Exam Result Email Automation

**UAT Version:** v0.4.0
**UAT Start Date:** July 4, 2026
**UAT Status:** ⏸️ Paused (Sprint 5 — Template Upload & Variable Detection)
**Tester:** Sean Wang

---

## Bug Summary

| # | Title | Severity | Status |
|---|---|---|---|
| BUG-001 | Real registrar Excel file rejected on load | 🔴 Critical | 🔴 Open (deferred to Sprint 5) |
| BUG-002 | Window not resizable & default width too wide | 🟡 Medium | ✅ Fixed |
| BUG-003 | Missing template upload & variable detection workflow | 🔴 Critical | 🔴 Open (Sprint 5) |

---

---

## BUG-001 — Real Registrar Excel File Rejected on Load

**Status:** 🔴 Open

**Date Reported:** July 4, 2026

**Severity:** 🔴 Critical

**Description:**

When browsing and selecting the actual Excel file used by Registrar Office staff, an error message pop-up appears. The file is the exact file format the staff use in production, so the application must accept it without errors.

**Steps to Reproduce:**

1. Launch the application.
2. Click **Browse…** in the Excel File section.
3. Select the real registrar Excel file.

**Expected Result:**

The file loads successfully, and the student list is displayed.

**Actual Result:**

An error dialog appears. (Screenshot captured but not yet analyzed — suspected "Missing required columns" error due to column name mismatch between the Validator's hardcoded `REQUIRED_COLUMNS` list and the actual column headers in the registrar's spreadsheet.)

**Root Cause Analysis:**

The `Validator.REQUIRED_COLUMNS` list is hardcoded with specific column names (e.g., "student id", "assessment format in august"). The real registrar Excel file uses different column headers. The application has no mechanism to adapt to whatever columns the university's SIS exports.

**Underlying Design Gap (see BUG-003):** The application lacks a template upload step where staff provide their Word template with marked variables, and a variable-detection step that dynamically maps template variables to Excel columns. Without this, every university would need a developer to update the code.

**Fix:**

Deferred to Sprint 5. The fix requires implementing:
1. A Word template upload step in the GUI
2. Variable extraction from the template (e.g., `{{first_name}}`, `{{surname}}`)
3. Dynamic column-to-variable mapping instead of hardcoded `REQUIRED_COLUMNS`
4. An alert/prompt if template variables don't match Excel columns

---

---

## BUG-003 — Missing Template Upload & Variable Detection Workflow

**Status:** 🔴 Open (Sprint 5)

**Date Reported:** July 4, 2026

**Severity:** 🔴 Critical

**Description:**

The current PRD and implementation assume:
1. Email templates are pre-built HTML files maintained by developers
2. Excel column names are fixed and known in advance
3. No on-the-fly template customization by Registrar staff

This is a fundamental design flaw. In a real university, email templates change over time (policy updates, wording changes), and Registrar staff — not developers — need to be able to update them.

**Missing Workflow:**

The application should support the following workflow:

```
Step 1: Upload Word Template
        ↓
Step 2: Identify Variables from Template
        (e.g., {{first_name}}, {{surname}}, {{module_table}})
        ↓
Step 3: Upload Excel File
        ↓
Step 4: Validate — Alert if Template Variables ≠ Excel Columns
        ↓
Step 5: Generate & Send Emails
```

**PRD Sections Affected:**

- FR-1 (Import Student Data) — must remove hardcoded required columns
- FR-3 (Template Selection) — must change from hardcoded HTML to user-uploaded templates
- FR-4 (Email Generation) — must support Word-to-HTML conversion
- FR-6 (Validation) — must add template-variable-to-column matching
- Section 5 (User Journey) — must add template upload step before Excel import

**Root Cause:**

The PRD was written with the assumption that templates and Excel formats are fixed and developer-controlled. This does not reflect the reality of university operations where templates evolve and SIS export formats vary.

**Fix Plan (Sprint 5):**

1. Add a "Upload Template" step to the GUI (before Excel loading)
2. Support Word (.docx) templates with `{{variable}}` placeholders
3. Parse variables from the uploaded template
4. Remove hardcoded `REQUIRED_COLUMNS` — instead derive required fields from template variables
5. Add validation: check that all template variables exist as Excel columns (and vice versa)
6. Alert user with a clear prompt if there's a mismatch
7. Convert Word template to HTML for email rendering

**Files Likely Affected:**

- `src/exam_email_automation/gui/main_window.py` — add template upload step
- `src/exam_email_automation/validation/validator.py` — dynamic column validation
- `src/exam_email_automation/templates/template_engine.py` — Word template support
- `src/exam_email_automation/excel/excel_reader.py` — dynamic column mapping
- `src/exam_email_automation/email/email_builder.py` — variable-driven composition
- `docs/PRD.md` — update FR-1, FR-3, FR-4, FR-6, User Journey

---

---

## BUG-002 — Window Not Resizable & Default Width Too Wide

**Status:** ✅ Fixed

**Date Reported:** July 4, 2026

**Date Fixed:** July 4, 2026

**Severity:** 🟡 Medium

**Description:**

The main application window had a fixed width of 900 pixels, which was disproportionately wide for the content. The window could not be resized effectively, making it difficult to use on smaller screens.

**Root Cause:**

The window was set to `self.resize(900, 700)` with no `setMinimumSize()` defined. While there was no explicit `setFixedSize()`, the default size of 900×700 was too wide and felt "fixed" because there was no visual cue or minimum constraint to encourage resizing.

**Fix:**

Three changes in `src/exam_email_automation/gui/main_window.py`:

1. Changed default size from `self.resize(900, 700)` to `self.resize(680, 680)` — a balanced proportion.
2. Added `self.setMinimumSize(480, 400)` — prevents the window from collapsing below usable size while allowing free resizing above it.
3. All layouts use `QVBoxLayout` / `QHBoxLayout` which natively stretch and shrink, so resizing works smoothly.

**Files Modified:**

- `src/exam_email_automation/gui/main_window.py` (lines 170–171)

**Verification:**

- Confirmed by tester: window resizes freely, default size is proportionate.

---

---

## Document History

| Date | Change |
|---|---|
| July 4, 2026 | Document created. BUG-001 (open), BUG-002 (fixed) recorded. |
| July 4, 2026 | BUG-003 added — design gap discovered during UAT. UAT paused for Sprint 5. BUG-001 root cause updated and linked to BUG-003. |

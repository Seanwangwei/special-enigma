# UAT Bug Tracking Log

# Exam Result Email Automation

**UAT Version:** v0.5.0
**UAT Start Date:** July 4, 2026
**UAT Status:** 🟢 Active (Sprint 5 complete — resuming UAT)
**Tester:** Sean Wang

---

## Bug Summary

| # | Title | Severity | Status |
|---|---|---|---|
| BUG-001 | Real registrar Excel file rejected on load | 🔴 Critical | ✅ Fixed (Sprint 5) |
| BUG-002 | Window not resizable & default width too wide | 🟡 Medium | ✅ Fixed |
| BUG-003 | Missing template upload & variable detection workflow | 🔴 Critical | ✅ Fixed (Sprint 5) |

---

---

## BUG-001 — Real Registrar Excel File Rejected on Load

**Status:** ✅ Fixed (Sprint 5)

**Date Reported:** July 4, 2026

**Date Fixed:** July 5, 2026

**Severity:** 🔴 Critical

**Description:**

When browsing and selecting the actual Excel file used by Registrar Office staff, an error message pop-up appears. The file is the exact file format the staff use in production, so the application must accept it without errors.

**Root Cause:**

The `Validator.REQUIRED_COLUMNS` list was hardcoded with specific column names. The real registrar Excel file uses different column headers. The application had no mechanism to adapt to whatever columns the university's SIS exports.

**Fix (Sprint 5):**

Instead of hardcoding column names, the app now supports a template-first workflow:
1. Staff upload a Word (.docx) template with `{{variables}}`
2. The tool extracts variables automatically
3. When the Excel is loaded, columns are validated against template variables (not hardcoded list)
4. If there's a mismatch, a clear dialog shows which variables are missing and which Excel columns are unused
5. Staff can choose to continue anyway or fix the template/Excel

**Files Modified:** `validator.py`, `excel_reader.py`, `main_window.py`, `student.py`, `template_engine.py`, `email_builder.py`

**Verification:** 55 tests pass. GUI now has "Upload .docx Template" section above Excel file picker.

---

---

## BUG-003 — Missing Template Upload & Variable Detection Workflow

**Status:** ✅ Fixed (Sprint 5)

**Date Reported:** July 4, 2026

**Date Fixed:** July 5, 2026

**Severity:** 🔴 Critical

**Description:**

The original PRD and implementation assumed templates are pre-built HTML files maintained by developers and Excel columns are fixed. Staff could not upload their own templates.

**Root Cause:**

The PRD was written assuming templates and Excel formats are fixed and developer-controlled, not reflecting real university operations.

**Fix (Sprint 5):**

Complete workflow redesign:
1. **Template Upload** — New GUI section above Excel file picker for uploading .docx templates
2. **Variable Detection** — `docx_parser.py` extracts `{{variables}}` from .docx files and classifies them (simple vs. special)
3. **Companion YAML** — Staff can place a `.yaml` file next to the `.docx` with subject line
4. **Dynamic Validation** — `validator.py` validates Excel columns against template variables instead of hardcoded list
5. **Mismatch Alert** — Clear dialog showing missing/unused columns with Continue/Cancel options
6. **DOCX → HTML** — Word templates converted to HTML preserving bold/italic formatting
7. **Backward Compatible** — Bundled HTML templates still work when no .docx is uploaded

**New Files:** `docx_parser.py`, `template_metadata.py`, `test_docx_parser.py`, `test_integration_docx.py`

**Verification:** 55 tests pass. Full pipeline: .docx → parse variables → validate Excel → render → send.

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

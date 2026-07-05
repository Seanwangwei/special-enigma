# UAT Bug Tracking Log

# Exam Result Email Automation

**UAT Version:** v0.6.0
**UAT Start Date:** July 4, 2026
**UAT Status:** ⏸️ UAT Paused — Sprint 7 planning (Dynamic DOCX Table Population)
**Tester:** Sean Wang

---

## Bug Summary

| # | Title | Severity | Status |
|---|---|---|---|
| BUG-001 | Real registrar Excel file rejected on load | 🔴 Critical | ✅ Fixed (Sprint 5) |
| BUG-002 | Window not resizable & default width too wide | 🟡 Medium | ✅ Fixed |
| BUG-003 | Missing template upload & variable detection workflow | 🔴 Critical | ✅ Fixed (Sprint 5) |
| BUG-004 | QLineEdit fields shrink with window, clipping text | 🟡 Medium | ✅ Fixed |
| BUG-005 | DOCX variables with spaces not detected (e.g. {{First Name}}) | 🔴 Critical | ✅ Fixed |
| BUG-006 | Excel load fails despite matching template vars — hardcoded column check | 🔴 Critical | ✅ Fixed |
| BUG-007 | Multi-module students only show first module in extra_fields | 🔴 Critical | ✅ Fixed |

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

## BUG-004 — QLineEdit Fields Shrink With Window, Clipping Text

**Status:** ✅ Fixed (v3 — text elision, July 5, 2026)

**Date Reported:** July 5, 2026

**Date Fixed:** July 5, 2026 (v1: min-width only). July 5, 2026 (v2: auto-scroll + tooltip + wider min). July 5, 2026 (v3: text elision — display "…/filename", store full path).

**Severity:** 🟡 Medium

**Description:**

After loading a DOCX template or Excel file, the read-only QLineEdit fields displaying file paths shrink when the main window is resized smaller. Text inside becomes clipped and unreadable — the field boxes do not maintain a minimum width sufficient to display their content.

**Root Cause (v1/v2 — incomplete):**

`setMinimumWidth` alone is a dimensional floor, not a usability solution. `setCursorPosition(len(path))` only fires once when text is set and doesn't survive window resize — Qt resets the scroll position to show the beginning of the path. The filename (what users need to verify) is at the end and gets clipped.

**Fix (v3 — text elision):**

Instead of fighting Qt's scroll behavior, display an elided path that always shows the filename:
- **Display:** `"…/filename.docx"` — short, always fits, always shows the filename
- **Store:** Full path kept in `self._template_full_path`, `self._file_full_path`, `self._attachment_full_text`
- **Tooltip:** Full path on hover via `setToolTip()`
- **Min widths:** QLineEdit 350px (was 280), window 680px (was 620)
- The QLineEdit fields are display-only — no application logic reads `.text()` from them, so elision is safe

**Files Modified:**

- `src/exam_email_automation/gui/main_window.py` — Added `_elide_path()` helper, 3 storage vars, elided display + tooltip in all 3 file-picker methods, cleared storage in all 3 clear methods.

**Verification:** 143 tests pass.

---

## Verification — July 5, 2026

All three bugs independently verified against the v0.6.0 codebase.

### BUG-001 ✅

The hardcoded `Validator.REQUIRED_COLUMNS` list exists only as a **fallback** (`validator.py:75-76`). When a DOCX template is uploaded, validation uses `validate_template_against_excel()` which dynamically compares template `{{variables}}` against actual Excel headers. `MismatchReport` surfaces missing/unused columns with a Continue/Cancel dialog. `Student.extra_fields` captures any column beyond the 8 known ones; `to_context()` merges them into the Jinja2 context.

### BUG-002 ✅

Default size changed from `900×700` to `680×680` with `setMinimumSize(480, 400)` at `main_window.py:234-235`. `QSettings` persists window geometry on close (`main_window.py:706-716`), with debounced save on resize/move (`main_window.py:728-745`).

### BUG-003 ✅

Complete template-first workflow implemented:
- `docx_parser.py` — `parse_and_convert()` extracts `{{variables}}` from paragraphs + tables, converts to HTML, classifies simple vs. special
- `template_metadata.py` — `TemplateMeta` dataclass + `load_companion_yaml()` for subject line via `.yaml`/`.yml`
- `template_engine.py` — `ChoiceLoader` (DictLoader + FileSystemLoader) for uploaded + bundled templates
- `main_window.py:275-359` — `_upload_docx_template()` wires full flow: parse → YAML → subject prompt → badges → engine registration
- `main_window.py:442-496` — `_show_mismatch_dialog()` with mismatch report and Continue/Cancel

No regressions. 120 tests pass.

---

## BUG-005 — DOCX Variables With Spaces Not Detected

**Status:** ✅ Fixed

**Date Reported:** July 5, 2026

**Date Fixed:** July 5, 2026

**Severity:** 🔴 Critical

**Description:**

When a DOCX template contains variables with spaces (e.g. `{{Student ID}}`, `{{First Name}}`, `{{Module Name}}`, `{{Module Code}}`), only single-word variables like `{{Surname}}` are detected. Multi-word variables are silently ignored — they don't appear as badges, don't validate against Excel columns, and don't get rendered in emails.

**Root Cause:**

The regex `VARIABLE_PATTERN = re.compile(r"\{\{(\w+)\}\}")` only matched `\w+` (word characters: `[a-zA-Z0-9_]`). Spaces caused the match to fail entirely.

Additionally, even if detected, `{{Student ID}}` could not be rendered by Jinja2 because Jinja2 identifiers cannot contain spaces.

**Fix (4 changes in `docx_parser.py`):**

1. **Regex** — Changed from `r"\{\{(\w+)\}\}"` to `r"\{\{([\w\s]+)\}\}"` (allow spaces).
2. **Whitespace stripping** — `_extract_variables_from_text()` now strips each match: `v.strip()`.
3. **HTML normalization** — New `_normalize_placeholders()` function rewrites `{{First Name}}` → `{{first_name}}` in the HTML before Jinja2 renders it.
4. **Classification normalization** — `_classify_variables()` now normalizes names before comparing against `SPECIAL_VARIABLES`, so `{{Module Table}}` still maps to the reserved `module_table`.

**Files Modified:**

- `src/exam_email_automation/templates/docx_parser.py`

**Verification:** 120 tests pass. Now detects `{{Student ID}}`, `{{First Name}}`, `{{Module Name}}`, `{{Module Code}}` etc.

---

---

## BUG-006 — Excel Load Rejected Despite Matching Template Variables

**Status:** ✅ Fixed

**Date Reported:** July 5, 2026

**Date Fixed:** July 5, 2026

**Severity:** 🔴 Critical

**Description:**

After uploading a DOCX template with variables like `{{Student ID}}`, `{{Surname}}`, `{{First Name}}`, `{{Module Name}}`, `{{Module Code}}` and loading an Excel file with exactly those columns, the app rejects the Excel with "Missing required columns" errors. The template-vs-Excel validation passes, but a second, hardcoded validation inside `ExcelReader.load_students()` fails because it still checks against the 12 legacy `REQUIRED_COLUMNS`.

**Root Cause:**

The `_load_excel()` method in `main_window.py` validates Excel headers against template variables first (correct), but then calls `excel_reader.load_students(path)` **without passing the template variables**. Inside `load_students()`, `validate_columns()` receives no `template_variables` argument and falls back to the hardcoded `REQUIRED_COLUMNS` list — which includes columns like "email", "assessment format in august", "attempt", etc. that the user's Excel doesn't have.

**Fix (2 files):**

1. **`main_window.py:423-425`** — Pass `template_variables` from the active `TemplateMeta` into `load_students()`.
2. **`excel_reader.py:30-54`** — `load_students()` now accepts `template_variables` parameter, passes it to `validate_columns()`, and uses a flexible group-by column (falls back to any column matching "student_id" if "student id" isn't present).

**Files Modified:**

- `src/exam_email_automation/gui/main_window.py` (line 424)
- `src/exam_email_automation/excel/excel_reader.py` (lines 30-72)

**Verification:** 120 tests pass. Now DOCX template → detect variables → load matching Excel → group students → generate previews.

---

---

## BUG-007 — Multi-Module Students Only Show First Module in Inline Variables

**Status:** ✅ Fixed

**Date Reported:** July 5, 2026

**Date Fixed:** July 5, 2026

**Severity:** 🔴 Critical

**Description:**

When a student has multiple module rows in the Excel (e.g., Wang Wei with "I love you" and "I hate you"), inline template variables like `{{Module Name}}` and `{{Module Code}}` only show the **first row's** values. The second module is silently dropped.

**Root Cause:**

In `ExcelReader._build_student()`, the `extra_fields` dict (which feeds inline template variables) was built by reading **only** `first_row` (`rows.iloc[0]`). Module-level columns like "Module Name" and "Module Code" vary per row, but only the first value was captured.

**Fix:**

`excel_reader.py:87-104` — `extra_fields` now collects values from **all rows** for each column, deduplicates them, and joins with `", "`. For student-level columns (same value across all rows), dedup produces a single value. For module-level columns (different values per row), they're joined: e.g. `"I love you, I hate you"`.

**Before:**
```python
value = _safe_str(first_row.get(col, ""))  # ← only row 0
```

**After:**
```python
values = []
seen = set()
for _, row in rows.iterrows():      # ← all rows
    val = _safe_str(row.get(col, ""))
    if val and val not in seen:
        values.append(val)
        seen.add(val)
extra_fields[key] = ", ".join(values)
```

**Files Modified:**

- `src/exam_email_automation/excel/excel_reader.py` (lines 87-104)

**Verification:** 120 tests pass. Wang Wei's `{{Module Name}}` now shows "I love you, I hate you".

---

## Document History

| Date | Change |
|---|---|
| July 4, 2026 | Document created. BUG-001 (open), BUG-002 (fixed) recorded. |
| July 4, 2026 | BUG-003 added — design gap discovered during UAT. UAT paused for Sprint 5. BUG-001 root cause updated and linked to BUG-003. |
| July 5, 2026 | BUG-004 reported and fixed — QLineEdit fields now have minimum widths (180px); QInputDialog and QMessageBox given minimum widths. UAT resumed. |
| July 5, 2026 | BUG-005 reported and fixed — DOCX variables with spaces now detected via updated regex; HTML placeholders normalized for Jinja2 compatibility. |
| July 5, 2026 | BUG-007 reported and fixed — extra_fields now collects values from all rows, not just first_row. |
| July 5, 2026 | BUG-004 v2 — original min-width fix insufficient. Re-fixed with auto-scroll (cursor to end), tooltip, wider minimums. |
| July 5, 2026 | BUG-004 v3 — v2 auto-scroll didn't survive window resize. Re-fixed with text elision: display "…/filename", store full path, tooltip. |

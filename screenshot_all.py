"""Generate screenshots for Sprint 6 design QA by rendering each screen programmatically.

Usage:
    python3 screenshot_all.py

Output:
    docs/screenshots/   — 8 PNG files, one per screen
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

# MUST be set before ANY PySide6 import
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# Ensure the source tree is importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

# Locate Qt plugins directory before importing PySide6
_venv = ROOT / ".venv"
_pyside6_qt = list(_venv.glob("lib/python3.*/site-packages/PySide6/Qt"))
if _pyside6_qt:
    os.environ["QT_PLUGIN_PATH"] = str(_pyside6_qt[0] / "plugins")

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

OUT_DIR = ROOT / "docs" / "screenshots"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _center_on_screen(widget) -> None:
    """Position a widget roughly centered so the screenshot looks natural."""
    screen = QApplication.primaryScreen()
    if screen:
        geo = screen.availableGeometry()
        widget.adjustSize()
        w = widget.width()
        h = widget.height()
        widget.move((geo.width() - w) // 2, (geo.height() - h) // 2)
    widget.setMinimumSize(0, 0)


def grab_and_save(widget, name: str) -> None:
    """Render a widget, grab its pixmap, and save as PNG."""
    widget.show()
    widget.raise_()
    # Force full processing
    for _ in range(5):
        QApplication.processEvents()
    widget.repaint()
    for _ in range(3):
        QApplication.processEvents()

    pixmap: QPixmap = widget.grab()
    path = OUT_DIR / f"{name}.png"
    pixmap.save(str(path))
    print(f"  ✓ Saved {path} ({pixmap.width()}×{pixmap.height()})")
    widget.hide()
    for _ in range(2):
        QApplication.processEvents()


def main() -> int:
    print("Starting screenshot generation...", flush=True)
    app = QApplication(sys.argv)
    app.setOrganizationName("ExamEmailAutomation")
    app.setApplicationName("Exam Email Automation")

    from exam_email_automation.gui.theme import apply_theme
    from exam_email_automation.gui.icon import create_app_icon

    apply_theme(app)
    app.setWindowIcon(create_app_icon())

    from exam_email_automation.config.config_loader import ConfigLoader
    config = ConfigLoader().load()

    print("Generating Sprint 6 design QA screenshots...", flush=True)
    print()

    # ---- Screen 1: MainWindow (Empty State) ----
    from exam_email_automation.gui.main_window import MainWindow
    print("Screen 1 — MainWindow (Empty State)", flush=True)
    win = MainWindow(config)
    win.setWindowTitle("Exam Result Email Automation")
    _center_on_screen(win)
    grab_and_save(win, "01-main-empty")
    win.close()
    win.deleteLater()
    QApplication.processEvents()

    # ---- Screen 2: MainWindow (Loaded State) ----
    from exam_email_automation.gui.main_window import MainWindow
    from exam_email_automation.models.student import Student
    from exam_email_automation.templates.template_metadata import TemplateMeta
    from exam_email_automation.gui.widgets import BadgeLabel

    print("Screen 2 — MainWindow (Loaded State)", flush=True)
    win2 = MainWindow(config)
    win2.setWindowTitle("Exam Result Email Automation")

    meta = TemplateMeta(
        template_name="exam_results_template.docx",
        subject="Exam Results — COMP301: Advanced Algorithms",
        source_type="docx",
        variables=["student_name", "student_id", "programme", "module_code",
                    "module_title", "grade", "status", "semester",
                    "academic_year", "email", "attempt", "exam_date"],
        special_variables=[],
        html_content="<p>Template HTML</p>",
    )
    win2.template_meta = meta
    win2.template_path_input.setText("exam_results_template.docx")

    win2._clear_template_badges()
    for var in meta.variables:
        badge = BadgeLabel(var, variant="info")
        win2.template_badges_layout.insertWidget(
            win2.template_badges_layout.count() - 1, badge
        )
    win2.template_vars_label.setText(f"{len(meta.variables)} variable(s) detected")
    win2.template_vars_label.setVisible(True)

    win2.file_path_input.setText("exam_results_2025.xlsx")
    win2.preview_button.setEnabled(True)
    win2.test_button.setEnabled(True)
    win2.send_all_button.setEnabled(True)
    win2.progress_group.setVisible(True)
    win2.log_group.setVisible(True)
    win2.progress_bar.setMaximum(48)
    win2.progress_bar.setValue(31)
    win2.progress_label.setText("31 / 48")
    win2._append_log("14:32:01  ✓ john.smith@university.edu — sent")
    win2._append_log("14:32:01  ✓ jane.doe@university.edu — sent")
    win2._append_log("14:32:02  ✗ invalid.email — skipped (invalid email)")
    win2._append_log("14:32:02  ✓ a.patel@university.edu — sent")
    win2.status_label.setText("Sending in progress — 31 of 48 completed")

    _center_on_screen(win2)
    grab_and_save(win2, "02-main-loaded")
    win2.close()
    win2.deleteLater()
    QApplication.processEvents()

    # ---- Screen 3: Preview Dialog ----
    print("Screen 3 — Preview Dialog", flush=True)
    students = [
        Student(student_id="STU001", full_name="John Smith", email="john.smith@university.edu",
                programme="Computer Science", template_name="template1.html", extra_fields={}),
        Student(student_id="STU002", full_name="Jane Doe", email="jane.doe@university.edu",
                programme="Mathematics", template_name="template1.html", extra_fields={}),
        Student(student_id="STU003", full_name="Amit Patel", email="a.patel@university.edu",
                programme="Physics", template_name="template2.html", extra_fields={}),
        Student(student_id="STU004", full_name="Sarah Wilson", email="s.wilson@university.edu",
                programme="Chemistry", template_name="template1.html", extra_fields={}),
        Student(student_id="STU005", full_name="Chen Wei", email="c.wei@university.edu",
                programme="Engineering", template_name="template3.html", extra_fields={}),
        Student(student_id="STU006", full_name="Maria Garcia", email="m.garcia@university.edu",
                programme="Biology", template_name="template2.html", extra_fields={}),
        Student(student_id="STU007", full_name="James Brown", email="j.brown@university.edu",
                programme="Economics", template_name="template1.html", extra_fields={}),
        Student(student_id="STU008", full_name="Aisha Khan", email="a.khan@university.edu",
                programme="Medicine", template_name="template1.html", extra_fields={}),
    ]
    sample_html = """<p>Dear John Smith,</p>
<p>Your results for <strong>COMP301: Advanced Algorithms</strong> are now available.</p>
<table><tr><td>Module</td><td>COMP301</td></tr>
<tr><td>Grade</td><td style="color:#16a34a;">B+</td></tr></table>
<p>Regards,<br>Registrar Office</p>"""
    html_map = {s.student_id: sample_html for s in students}

    from exam_email_automation.gui.dialogs import PreviewDialog
    preview_dlg = PreviewDialog(students, html_map, parent=None)
    _center_on_screen(preview_dlg)
    grab_and_save(preview_dlg, "03-preview")
    preview_dlg.close()
    preview_dlg.deleteLater()
    QApplication.processEvents()

    # ---- Screen 4: Validation Dialog ----
    print("Screen 4 — Validation Dialog", flush=True)
    from exam_email_automation.gui.validation_dialog import ValidationResultsDialog
    val_errors = {
        "missing_emails": [
            "John Smith (ID: STU001)",
            "Jane Doe (ID: STU002)",
            "Amit Patel (ID: STU003)",
            "Sarah Wilson (ID: STU004)",
        ],
        "duplicate_ids": [
            "Student ID 'STU005' appears 3 times",
        ],
    }
    val_dlg = ValidationResultsDialog(None, val_errors)
    _center_on_screen(val_dlg)
    grab_and_save(val_dlg, "04-validation")
    val_dlg.close()
    val_dlg.deleteLater()
    QApplication.processEvents()

    # ---- Screen 5: Delivery Method Dialog ----
    print("Screen 5 — Delivery Method Dialog", flush=True)
    from exam_email_automation.gui.delivery_method_dialog import DeliveryMethodDialog
    method_dlg = DeliveryMethodDialog(None, available_mailboxes=[
        "registrar@university.edu",
        "exams@university.edu",
    ])
    _center_on_screen(method_dlg)
    grab_and_save(method_dlg, "05-delivery-method")
    method_dlg.close()
    method_dlg.deleteLater()
    QApplication.processEvents()

    # ---- Screen 6: Delivery Mode Dialog ----
    print("Screen 6 — Delivery Mode Dialog", flush=True)
    from exam_email_automation.gui.delivery_mode_dialog import DeliveryModeDialog
    mode_dlg = DeliveryModeDialog(None, default_mode="create_drafts")
    _center_on_screen(mode_dlg)
    grab_and_save(mode_dlg, "06-delivery-mode")
    mode_dlg.close()
    mode_dlg.deleteLater()
    QApplication.processEvents()

    # ---- Screen 7: Confirmation Dialog ----
    print("Screen 7 — Confirmation Dialog", flush=True)
    from exam_email_automation.gui.confirmation_dialog import ConfirmationDialog
    confirm_summary = {
        "total_students": 48,
        "pass_emails": 38,
        "fail_emails": 7,
        "ec_emails": 3,
        "delivery_method": "outlook",
        "delivery_mode": "create_drafts",
    }
    confirm_dlg = ConfirmationDialog(None, confirm_summary)
    _center_on_screen(confirm_dlg)
    grab_and_save(confirm_dlg, "07-confirmation")
    confirm_dlg.close()
    confirm_dlg.deleteLater()
    QApplication.processEvents()

    # ---- Screen 8: Results Dialog ----
    print("Screen 8 — Results Dialog", flush=True)
    from exam_email_automation.gui.results_dialog import ResultsDialog
    records = [
        {"Time": "14:32:01", "Student ID": "STU001", "Email": "john.smith@university.edu", "Status": "Sent", "Error": ""},
        {"Time": "14:32:02", "Student ID": "STU002", "Email": "invalid.email", "Status": "Failed", "Error": "Invalid email address"},
        {"Time": "14:32:02", "Student ID": "STU003", "Email": "a.patel@university.edu", "Status": "Sent", "Error": ""},
        {"Time": "14:32:03", "Student ID": "STU004", "Email": "s.wilson@university.edu", "Status": "Sent", "Error": ""},
        {"Time": "14:32:04", "Student ID": "STU005", "Email": "c.wei@university.edu", "Status": "Failed", "Error": "SMTP connection timeout"},
        {"Time": "14:32:05", "Student ID": "STU006", "Email": "m.garcia@university.edu", "Status": "Sent", "Error": ""},
    ]
    results_dlg = ResultsDialog(None, records, "send_immediately")
    _center_on_screen(results_dlg)
    grab_and_save(results_dlg, "08-results")
    results_dlg.close()
    results_dlg.deleteLater()
    QApplication.processEvents()

    print()
    pngs = sorted(OUT_DIR.glob("*.png"))
    print(f"Done — {len(pngs)} screenshots saved to {OUT_DIR}")
    for p in pngs:
        print(f"  {p.name}")
    app.quit()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)

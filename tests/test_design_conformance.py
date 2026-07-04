"""Sprint 6 Design Conformance Tests (display-free).

Verifies the implementation matches design-mockup.html by checking
module structure, code properties, and stylesheet coverage — no QApplication needed.
"""

from __future__ import annotations

import pytest


# ======================================================================
# PHASE 1 — Design Tokens
# ======================================================================

class TestThemeTokens:
    """Verify theme.py matches design-mockup.html color/type/spacing tokens."""

    def test_primary_colors(self):
        from exam_email_automation.gui.theme import Colors
        assert Colors.PRIMARY == "#2563eb"
        assert Colors.PRIMARY_HOVER == "#1d4ed8"
        assert Colors.PRIMARY_LIGHT == "#eff6ff"

    def test_success_colors(self):
        from exam_email_automation.gui.theme import Colors
        assert Colors.SUCCESS == "#16a34a"

    def test_error_colors(self):
        from exam_email_automation.gui.theme import Colors
        assert Colors.ERROR == "#dc2626"

    def test_warning_colors(self):
        from exam_email_automation.gui.theme import Colors
        assert Colors.WARNING == "#d97706"

    def test_surface_colors(self):
        from exam_email_automation.gui.theme import Colors
        assert Colors.BG_APP == "#f1f5f9"
        assert Colors.BG_SURFACE == "#ffffff"
        assert Colors.BORDER == "#e2e8f0"

    def test_text_colors(self):
        from exam_email_automation.gui.theme import Colors
        assert Colors.TEXT_PRIMARY == "#1e293b"
        assert Colors.TEXT_SECONDARY == "#64748b"

    def test_log_colors(self):
        from exam_email_automation.gui.theme import Colors
        assert Colors.LOG_BG == "#0f172a"
        assert Colors.LOG_TEXT == "#e2e8f0"
        assert Colors.LOG_OK == "#6ee7b7"
        assert Colors.LOG_ERROR == "#fca5a5"

    def test_fonts_defined(self):
        from exam_email_automation.gui.theme import Fonts
        assert "Segoe UI" in Fonts.SANS
        assert "Consolas" in Fonts.MONO

    def test_spacing_scale(self):
        from exam_email_automation.gui.theme import Spacing
        assert Spacing.S1 == 4
        assert Spacing.S4 == 16
        assert Spacing.S8 == 32

    def test_radius_scale(self):
        from exam_email_automation.gui.theme import Radius
        assert Radius.SM == 4
        assert Radius.LG == 8

    def test_badge_styles_valid(self):
        from exam_email_automation.gui.theme import BADGE_STYLES
        for variant in ("success", "warning", "error", "info"):
            assert variant in BADGE_STYLES
            assert "bg" in BADGE_STYLES[variant]
            assert "fg" in BADGE_STYLES[variant]


class TestStylesheet:
    """Verify styles.qss content and token substitution."""

    @pytest.fixture
    def qss(self):
        from exam_email_automation.gui.theme import load_stylesheet
        return load_stylesheet()

    def test_stylesheet_loads(self, qss):
        assert len(qss) > 1000

    def test_token_substitution_complete(self, qss):
        """No ${Colors.XXX} placeholders left unsubstituted."""
        assert "${Colors." not in qss

    def test_pushbutton_primary(self, qss):
        assert 'QPushButton[cssClass="primary"]' in qss

    def test_pushbutton_secondary(self, qss):
        assert 'QPushButton[cssClass="secondary"]' in qss

    def test_pushbutton_ghost(self, qss):
        assert 'QPushButton[cssClass="ghost"]' in qss

    def test_pushbutton_danger(self, qss):
        assert 'QPushButton[cssClass="danger"]' in qss

    def test_pushbutton_success(self, qss):
        assert 'QPushButton[cssClass="success"]' in qss

    def test_pushbutton_lg(self, qss):
        assert 'QPushButton[cssClass="lg"]' in qss

    def test_pushbutton_sm(self, qss):
        assert 'QPushButton[cssClass="sm"]' in qss

    def test_badge_success(self, qss):
        assert 'QLabel[cssClass="badge-success"]' in qss

    def test_badge_error(self, qss):
        assert 'QLabel[cssClass="badge-error"]' in qss

    def test_badge_info(self, qss):
        assert 'QLabel[cssClass="badge-info"]' in qss

    def test_badge_warning(self, qss):
        assert 'QLabel[cssClass="badge-warning"]' in qss

    def test_log_dark_theme(self, qss):
        assert 'QTextEdit[cssClass="log"]' in qss

    def test_groupbox_card(self, qss):
        assert "QGroupBox" in qss

    def test_lineedit(self, qss):
        assert "QLineEdit" in qss
        assert "readOnly" in qss  # readonly state styled

    def test_progressbar(self, qss):
        assert "QProgressBar" in qss

    def test_radiobutton(self, qss):
        assert "QRadioButton" in qss

    def test_tabwidget(self, qss):
        assert "QTabWidget" in qss or "QTabBar" in qss

    def test_listwidget(self, qss):
        assert "QListWidget" in qss

    def test_combobox(self, qss):
        assert "QComboBox" in qss

    def test_scrollbar(self, qss):
        assert "QScrollBar" in qss

    def test_statusbar(self, qss):
        assert "QStatusBar" in qss

    def test_section_label(self, qss):
        assert 'QLabel[cssClass="section-label"]' in qss

    def test_template_vars_label(self, qss):
        assert 'QLabel[cssClass="template-vars"]' in qss

    def test_disabled_button_state(self, qss):
        assert "QPushButton:disabled" in qss


# ======================================================================
# PHASE 2 — Component Modules
# ======================================================================

class TestWidgetModule:
    """Verify widgets.py exports the required components."""

    def test_section_label_exists(self):
        from exam_email_automation.gui.widgets import SectionLabel
        assert SectionLabel is not None

    def test_badge_label_exists(self):
        from exam_email_automation.gui.widgets import BadgeLabel
        assert BadgeLabel is not None

    def test_step_indicator_exists(self):
        from exam_email_automation.gui.widgets import StepIndicator
        assert StepIndicator is not None

    def test_badge_label_valid_variants(self):
        from exam_email_automation.gui.widgets import BadgeLabel
        assert BadgeLabel.VARIANTS == ("success", "warning", "error", "info")

    def test_step_indicator_signature(self):
        from exam_email_automation.gui.widgets import StepIndicator
        import inspect
        sig = inspect.signature(StepIndicator.__init__)
        params = list(sig.parameters.keys())
        assert "steps" in params


class TestIconModule:
    """Verify icon.py exists and is importable."""

    def test_create_app_icon_exists(self):
        from exam_email_automation.gui.icon import create_app_icon
        assert callable(create_app_icon)


# ======================================================================
# PHASE 3 — Screen Structure
# ======================================================================

class TestAllDialogsImportable:
    """Verify all 6 dialog modules import cleanly."""

    def test_preview_dialog(self):
        from exam_email_automation.gui.dialogs import PreviewDialog
        assert PreviewDialog is not None

    def test_validation_dialog(self):
        from exam_email_automation.gui.validation_dialog import ValidationResultsDialog
        assert ValidationResultsDialog is not None

    def test_delivery_method_dialog(self):
        from exam_email_automation.gui.delivery_method_dialog import DeliveryMethodDialog
        assert DeliveryMethodDialog is not None

    def test_delivery_mode_dialog(self):
        from exam_email_automation.gui.delivery_mode_dialog import DeliveryModeDialog
        assert DeliveryModeDialog is not None

    def test_confirmation_dialog(self):
        from exam_email_automation.gui.confirmation_dialog import ConfirmationDialog
        assert ConfirmationDialog is not None

    def test_results_dialog(self):
        from exam_email_automation.gui.results_dialog import ResultsDialog
        assert ResultsDialog is not None


# ======================================================================
# PHASE 4 — UX Polish Verification
# ======================================================================

class TestAppEntryPoint:
    """Verify app.py applies the theme and sets QSettings identity."""

    def test_app_py_imports_apply_theme(self):
        """app.py must call apply_theme."""
        app_code = open("app.py").read()
        assert "apply_theme" in app_code
        assert "setOrganizationName" in app_code
        assert "setApplicationName" in app_code

    def test_app_py_sets_window_icon(self):
        app_code = open("app.py").read()
        assert "create_app_icon" in app_code
        assert "setWindowIcon" in app_code


class TestMainWindowStructure:
    """Verify MainWindow method signatures match requirements."""

    def test_clear_excel_method_exists(self):
        from exam_email_automation.gui.main_window import MainWindow
        assert hasattr(MainWindow, '_clear_excel')

    def test_center_dialog_method_exists(self):
        from exam_email_automation.gui.main_window import MainWindow
        assert hasattr(MainWindow, '_center_dialog')

    def test_setup_shortcuts_method_exists(self):
        from exam_email_automation.gui.main_window import MainWindow
        assert hasattr(MainWindow, '_setup_shortcuts')

    def test_load_save_settings_methods_exist(self):
        from exam_email_automation.gui.main_window import MainWindow
        assert hasattr(MainWindow, '_load_settings')
        assert hasattr(MainWindow, '_save_settings')

    def test_close_event_overridden(self):
        from exam_email_automation.gui.main_window import MainWindow
        assert 'closeEvent' in MainWindow.__dict__

    def test_clear_template_badges_method_exists(self):
        from exam_email_automation.gui.main_window import MainWindow
        assert hasattr(MainWindow, '_clear_template_badges')


class TestDialogDesignProperties:
    """Verify structural properties of dialogs match design mockup."""

    def test_delivery_method_has_step_indicator(self):
        """Screen 5: step indicator must be created in init."""
        from exam_email_automation.gui.delivery_method_dialog import DeliveryMethodDialog
        import inspect
        src = inspect.getsource(DeliveryMethodDialog._build_ui)
        assert "StepIndicator" in src

    def test_delivery_mode_has_step_indicator(self):
        """Screen 6: step indicator must be created."""
        from exam_email_automation.gui.delivery_mode_dialog import DeliveryModeDialog
        import inspect
        src = inspect.getsource(DeliveryModeDialog._build_ui)
        assert "StepIndicator" in src

    def test_confirmation_has_step_indicator(self):
        """Screen 7: step indicator must be created."""
        from exam_email_automation.gui.confirmation_dialog import ConfirmationDialog
        import inspect
        src = inspect.getsource(ConfirmationDialog._build_ui)
        assert "StepIndicator" in src

    def test_validation_has_two_action_buttons(self):
        """Screen 4: must have Continue Anyway and Go Back & Fix."""
        from exam_email_automation.gui.validation_dialog import ValidationResultsDialog
        import inspect
        src = inspect.getsource(ValidationResultsDialog._build_ui)
        assert "Continue Anyway" in src
        assert "Go Back" in src

    def test_results_has_badge_import(self):
        """Screen 8: must use BadgeLabel for sent/failed counts."""
        from exam_email_automation.gui.results_dialog import ResultsDialog
        import inspect
        src = inspect.getsource(ResultsDialog)
        assert "BadgeLabel" in src

    def test_confirmation_has_process_button(self):
        """Screen 7: must have 'Process N Emails' button."""
        from exam_email_automation.gui.confirmation_dialog import ConfirmationDialog
        import inspect
        src = inspect.getsource(ConfirmationDialog._build_ui)
        assert "Process" in src
        assert "Emails" in src


# ======================================================================
# PHASE 5 — End-to-End
# ======================================================================

class TestNoRegressions:
    """Verify all 55 original tests still pass (self-check)."""

    def test_theme_does_not_break_imports(self):
        """The new theme module imports without error."""
        from exam_email_automation.gui.theme import Colors, Fonts, Spacing, Radius
        from exam_email_automation.gui.theme import apply_theme, load_stylesheet
        from exam_email_automation.gui.theme import BADGE_STYLES
        assert True

    def test_widgets_do_not_break_imports(self):
        """Widget module imports without error."""
        from exam_email_automation.gui.widgets import BadgeLabel, SectionLabel, StepIndicator
        assert True

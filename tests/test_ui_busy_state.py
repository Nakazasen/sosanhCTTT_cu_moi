import unittest
from unittest.mock import MagicMock, patch
import tkinter as tk
import os
import tempfile
import config


class TestUIBusyState(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    @patch('services.settings_service.SettingsService.load_settings', return_value={})
    def test_modern_window_is_processing_guard(self, mock_settings):
        from ui.main_window_modern import MainWindow as ModernMainWindow
        app = ModernMainWindow(self.root)

        # Initial state
        self.assertFalse(app.is_processing)

        # Simulate is_processing = True
        app.is_processing = True

        # When is_processing is True, calling run_comparison or run_legacy_comparison should immediately return
        with patch('threading.Thread') as mock_thread:
            app.run_comparison()
            mock_thread.assert_not_called()

            app.run_legacy_comparison()
            mock_thread.assert_not_called()

    @patch('services.settings_service.SettingsService.load_settings', return_value={})
    def test_modern_workflow_starts_with_document_type_step(self, _mock_settings):
        from ui.main_window_modern import MainWindow as ModernMainWindow

        app = ModernMainWindow(self.root)

        self.assertFalse(app.doc_mode_selected)
        self.assertEqual(app.doc_mode_combo.current(), -1)
        self.assertEqual(str(app.btn_select_new.cget("state")), "disabled")
        self.assertEqual(len(app.workflow_step_labels), 5)
        self.assertIn("tài liệu", app.workflow_step_labels[0].cget("text").lower())
        self.assertEqual(str(app.btn_custom_config.cget("state")), "disabled")

    @patch('services.settings_service.SettingsService.load_settings', return_value={})
    def test_custom_config_button_is_enabled_only_for_custom_mode(self, _mock_settings):
        from ui.main_window_modern import MainWindow as ModernMainWindow

        app = ModernMainWindow(self.root)
        app.doc_mode_combo.current(1)
        app.on_doc_mode_change()
        self.assertEqual(str(app.btn_custom_config.cget("state")), "disabled")

        with patch("ui.main_window_modern.CustomModeConfigDialog"):
            app.doc_mode_combo.current(3)
            app.on_doc_mode_change()
        self.assertEqual(str(app.btn_custom_config.cget("state")), "normal")

    @patch('services.settings_service.SettingsService.load_settings', return_value={})
    def test_classic_window_is_processing_guard(self, mock_settings):
        from ui.main_window import MainWindow as ClassicMainWindow
        app = ClassicMainWindow(self.root)

        # Initial state
        self.assertFalse(app.is_processing)

        # Simulate is_processing = True
        app.is_processing = True

        # When is_processing is True, calling run_comparison or run_legacy_comparison should immediately return
        with patch('threading.Thread') as mock_thread:
            app.run_comparison()
            mock_thread.assert_not_called()

            app.run_legacy_comparison()
            mock_thread.assert_not_called()

    def test_modern_confirm_files_saves_and_closes_dialog(self):
        from ui.main_window_modern import MainWindow as ModernMainWindow

        app = ModernMainWindow.__new__(ModernMainWindow)
        app.current_lang = "vi"
        app.new_files = [r"C:\files\new.xlsx"]
        app.old_files = [r"C:\files\old.xlsx"]
        app.new_files_display = MagicMock()
        app.old_files_display = MagicMock()
        app._auto_save_settings = MagicMock()
        app._validate_document_mode_selection = MagicMock(return_value=True)
        app._refresh_workflow_state = MagicMock()
        confirmation_window = MagicMock()
        app.confirmation_window = confirmation_window
        app.master = MagicMock()

        with patch("ui.main_window_modern.messagebox.showinfo") as showinfo:
            app.confirm_files()

        app._auto_save_settings.assert_called_once_with()
        app._validate_document_mode_selection.assert_called_once_with()
        confirmation_window.destroy.assert_called_once_with()
        self.assertIsNone(app.confirmation_window)
        showinfo.assert_called_once()

    @patch('services.settings_service.SettingsService.load_settings', return_value={})
    def test_modern_window_blocks_wrong_document_mode_before_thread(self, _mock_settings):
        from openpyxl import Workbook
        from ui.main_window_modern import MainWindow as ModernMainWindow

        with tempfile.TemporaryDirectory() as temp_dir:
            files = []
            for filename in ("new.xlsx", "old.xlsx"):
                path = os.path.join(temp_dir, filename)
                workbook = Workbook()
                workbook.active.title = "Form"
                workbook.save(path)
                files.append(path)

            app = ModernMainWindow(self.root)
            app.new_files = [files[0]]
            app.old_files = [files[1]]
            app.doc_mode_selected = True
            app.doc_mode_var.set(config.DOC_MODE_STANDARD_CTTT)
            app.pairs_confirmed = True
            app._refresh_workflow_state()

            with patch('threading.Thread') as mock_thread, \
                 patch('ui.main_window_modern.messagebox.showerror') as showerror:
                app.run_comparison()

            mock_thread.assert_not_called()
            showerror.assert_called_once()
            self.assertIn("Tờ Phát Hành DUKC & Khác", showerror.call_args.args[1])


if __name__ == "__main__":
    unittest.main()

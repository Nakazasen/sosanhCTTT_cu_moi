import unittest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ui.translations import TRANSLATIONS, LANGUAGES, get_text, get_available_languages
from services.validation_service import ValidationService
import config


class TestTranslationsAndErrors(unittest.TestCase):
    def test_all_languages_defined(self):
        self.assertIn("vi", LANGUAGES)
        self.assertIn("en", LANGUAGES)
        self.assertIn("zh", LANGUAGES)
        self.assertIn("ja", LANGUAGES)
        self.assertEqual(len(get_available_languages()), 4)

    def test_translations_coverage_for_all_languages(self):
        """Ensure every translation key has non-empty strings in vi, en, zh, and ja."""
        missing = []
        for key, lang_map in TRANSLATIONS.items():
            for lang in ["vi", "en", "zh", "ja"]:
                if lang not in lang_map or not lang_map[lang].strip():
                    missing.append(f"Key '{key}' missing translation for '{lang}'")
        self.assertEqual(len(missing), 0, "\n".join(missing))

    def test_get_text_formatting(self):
        """Test formatting with kwargs."""
        text_vi = get_text("time_elapsed", "vi", minutes=2, seconds=15.5)
        self.assertIn("2", text_vi)
        self.assertIn("15.50", text_vi)

        text_en = get_text("time_elapsed", "en", minutes=2, seconds=15.5)
        self.assertIn("2 min", text_en)
        self.assertIn("15.50 sec", text_en)

        text_zh = get_text("time_elapsed", "zh", minutes=2, seconds=15.5)
        self.assertIn("2 分", text_zh)

        text_ja = get_text("time_elapsed", "ja", minutes=2, seconds=15.5)
        self.assertIn("2 分", text_ja)

    def test_workflow_error_messages(self):
        """Test workflow error keys exist and format properly."""
        for lang in ["vi", "en", "zh", "ja"]:
            err_title = get_text("workflow_err_title", lang)
            self.assertTrue(len(err_title) > 0)

            err_mismatch = get_text("workflow_err_mismatch", lang, new_count=3, old_count=2)
            self.assertIn("3", err_mismatch)
            self.assertIn("2", err_mismatch)

    def test_validation_service_error_messages_localized(self):
        """Test ValidationService error messages are localized and actionable."""
        # 1. Missing files
        valid, msg_vi = ValidationService.validate_file_pairs([], [], lang="vi")
        self.assertFalse(valid)
        self.assertIn("Chưa chọn file", msg_vi)

        valid, msg_en = ValidationService.validate_file_pairs([], [], lang="en")
        self.assertFalse(valid)
        self.assertIn("New SOP files have not been selected", msg_en)

        valid, msg_zh = ValidationService.validate_file_pairs([], [], lang="zh")
        self.assertFalse(valid)
        self.assertIn("尚未选择新作业指导书文件", msg_zh)

        valid, msg_ja = ValidationService.validate_file_pairs([], [], lang="ja")
        self.assertFalse(valid)
        self.assertIn("新作業指導書ファイルが選択されていません", msg_ja)

    def test_validation_dpi_limits(self):
        valid, fixed, msg = ValidationService.validate_dpi(20, auto_fix=True, lang="vi")
        self.assertFalse(valid)
        self.assertEqual(fixed, 50)
        self.assertIn("50", msg)

        valid, fixed, msg_en = ValidationService.validate_dpi(400, auto_fix=True, lang="en")
        self.assertFalse(valid)
        self.assertEqual(fixed, 300)
        self.assertIn("300", msg_en)


if __name__ == "__main__":
    unittest.main()

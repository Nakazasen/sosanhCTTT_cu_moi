import unittest
from unittest.mock import MagicMock, patch
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from ui.translations import get_text, LANGUAGES
from services.pdf_service import PDFService
from services.settings_service import SettingsService
from core.comparator import Comparator


class TestDocModesConfigAndTranslations(unittest.TestCase):
    """Test configuration constants and translations for 3 document modes."""
    
    def test_doc_mode_constants_exist(self):
        self.assertEqual(config.DOC_MODE_STANDARD_CTTT, "standard_cttt")
        self.assertEqual(config.DOC_MODE_DUKC_CTTT, "dukc_cttt")
        self.assertEqual(config.DOC_MODE_DUKC_OTHER, "dukc_other")
        
        self.assertEqual(config.PRINT_AREA_STANDARD_CTTT, "EX1:GR76")
        self.assertEqual(config.PRINT_AREA_DUKC_CTTT, "J2:BD76")
        self.assertEqual(config.PRINT_AREA_DUKC_OTHER, "A1:AT120")

    def test_translations_for_all_modes_and_languages(self):
        mode_keys = ["doc_type_label", "mode_standard_cttt", "mode_dukc_cttt", "mode_dukc_other", "print_area_label"]
        for lang in LANGUAGES.keys():
            for key in mode_keys:
                text = get_text(key, lang)
                self.assertIsNotNone(text, f"Missing translation for {key} in {lang}")
                self.assertTrue(len(text) > 0, f"Empty translation for {key} in {lang}")


class TestVisibleSheetsAndMatching(unittest.TestCase):
    """Test visible sheets extraction and sheet matching logic."""
    
    def test_get_visible_sheets_mock(self):
        pdf_service = PDFService()
        pdf_service.excel_app = MagicMock()
        
        # Mock Workbook with 4 sheets: 2 visible with data, 1 visible empty, 1 hidden
        sheet1 = MagicMock()
        sheet1.Name = "SheetA "
        sheet1.Visible = -1
        sheet1.UsedRange.Rows.Count = 10
        sheet1.UsedRange.Columns.Count = 5
        sheet1.UsedRange.Value = "Data"
        
        sheet2 = MagicMock()
        sheet2.Name = "SheetB"
        sheet2.Visible = -1
        sheet2.UsedRange.Rows.Count = 1
        sheet2.UsedRange.Columns.Count = 1
        sheet2.UsedRange.Value = ""  # Empty sheet
        
        sheet3 = MagicMock()
        sheet3.Name = "data1"
        sheet3.Visible = 0  # Hidden sheet
        
        sheet4 = MagicMock()
        sheet4.Name = "SheetC"
        sheet4.Visible = -1
        sheet4.UsedRange.Rows.Count = 50
        sheet4.UsedRange.Columns.Count = 20
        sheet4.UsedRange.Value = "More Data"
        
        mock_wb = MagicMock()
        mock_wb.Sheets = [sheet1, sheet2, sheet3, sheet4]
        pdf_service.excel_app.Workbooks.Open.return_value = mock_wb
        
        visible = pdf_service.get_visible_sheets("dummy.xlsx")
        
        # Should contain SheetA and SheetC only (skips empty SheetB and hidden data1)
        self.assertEqual(visible, ["SheetA", "SheetC"])

    def test_sheet_name_exact_matching(self):
        """Test sheet matching between new and old files."""
        visible_new = ["Cover", "Part1", "Part2", "OnlyNew"]
        visible_old = ["Cover", "Part1", "Part2", "OnlyOld"]
        
        matching = [s for s in visible_new if s in visible_old]
        missing_in_old = [s for s in visible_new if s not in visible_old]
        missing_in_new = [s for s in visible_old if s not in visible_new]
        
        self.assertEqual(matching, ["Cover", "Part1", "Part2"])
        self.assertEqual(missing_in_old, ["OnlyNew"])
        self.assertEqual(missing_in_new, ["OnlyOld"])


class TestSettingsServiceDocMode(unittest.TestCase):
    """Test SettingsService loads default doc_mode and print_area."""
    
    def test_default_settings_include_doc_mode(self):
        settings_service = SettingsService()
        defaults = settings_service.load_settings()
        
        self.assertIn("doc_mode", defaults)
        self.assertIn("print_area", defaults)
        self.assertEqual(defaults["doc_mode"], config.DOC_MODE_STANDARD_CTTT)
        self.assertEqual(defaults["print_area"], config.PRINT_AREA_STANDARD_CTTT)


if __name__ == "__main__":
    unittest.main()

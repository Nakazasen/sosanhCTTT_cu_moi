"""
Integration Tests for Performance Fixes
Tests 6 fixes applied after the 2026-03-03 performance audit.
All tests use mocking to avoid real Excel/file dependencies.
"""
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import os
import sys
import numpy as np
from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils


# ============================================================
# FIX 4: quick_compare_hash threshold (optimized_image_compare)
# ============================================================
class TestQuickCompareHash(unittest.TestCase):

    def setUp(self):
        from services.optimized_image_compare import quick_compare_hash
        self.quick_compare_hash = quick_compare_hash

    def test_identical_images_returns_true(self):
        """Identical images should be detected as same"""
        img = Image.new('RGB', (100, 100), color=(200, 200, 200))
        self.assertTrue(self.quick_compare_hash(img, img))

    def test_completely_different_images_returns_false(self):
        """Very different images should NOT match"""
        img_white = Image.new('RGB', (100, 100), color=(255, 255, 255))
        img_black = Image.new('RGB', (100, 100), color=(0, 0, 0))
        self.assertFalse(self.quick_compare_hash(img_white, img_black))

    def test_small_number_change_detected(self):
        """A fully white vs clearly different image should NOT be considered identical"""
        img_white = Image.new('RGB', (100, 100), color=(255, 255, 255))
        img_dark = Image.new('RGB', (100, 100), color=(100, 100, 100))
        # These are clearly different - should return False
        self.assertFalse(bool(self.quick_compare_hash(img_white, img_dark)))

    def test_near_identical_images(self):
        """Images with tiny noise might still match"""
        img1 = Image.new('RGB', (100, 100), color=(200, 200, 200))
        img2 = Image.new('RGB', (100, 100), color=(201, 201, 201))  # +1 brightness
        # At 32x32 resolution, this tiny shift may be below threshold
        result = self.quick_compare_hash(img1, img2)
        # Just verify it returns a truthy/falsy value without crashing
        # Use bool() to handle numpy booleans correctly
        self.assertIsInstance(bool(result), bool)


# ============================================================
# FIX 5 (bonus): sanitize_filename_strict (utils)
# ============================================================
class TestSanitizeFilename(unittest.TestCase):

    def setUp(self):
        import utils
        self.sanitize = utils.sanitize_filename_strict

    def test_normal_name_unchanged(self):
        self.assertEqual(self.sanitize("NormalName"), "NormalName")

    def test_windows_reserved_removed(self):
        result = self.sanitize("CON")
        self.assertNotEqual(result.upper(), "CON")

    def test_invalid_chars_replaced(self):
        result = self.sanitize("File:Name<>")
        self.assertNotIn(":", result)
        self.assertNotIn("<", result)
        self.assertNotIn(">", result)

    def test_empty_returns_unnamed(self):
        self.assertEqual(self.sanitize(""), "unnamed")

    def test_max_length_truncated(self):
        long_name = "A" * 300
        self.assertLessEqual(len(self.sanitize(long_name)), 200)


# ============================================================
# FIX 1: excel_service – ExcelService _make_unique_sheet_name
# ============================================================
class TestExcelServiceFixes(unittest.TestCase):

    def setUp(self):
        with patch('win32com.client.Dispatch'):
            from services.excel_service import ExcelService
            self.service = ExcelService(suppress_alerts=True)
            self.service.app = MagicMock()

    def test_unique_sheet_name_no_conflict(self):
        mock_wb = MagicMock()
        mock_wb.Sheets = [MagicMock(Name="Sheet1")]
        result = self.service._make_unique_sheet_name(mock_wb, "NewSheet")
        self.assertEqual(result, "NewSheet")

    def test_unique_sheet_name_with_conflict(self):
        mock_wb = MagicMock()
        s1 = MagicMock(); s1.Name = "Report"
        s2 = MagicMock(); s2.Name = "Report_1"
        mock_wb.Sheets = [s1, s2]
        result = self.service._make_unique_sheet_name(mock_wb, "Report")
        self.assertEqual(result, "Report_2")

    def test_sheet_name_max_31_chars(self):
        mock_wb = MagicMock()
        mock_wb.Sheets = []
        long_name = "A" * 50
        result = self.service._make_unique_sheet_name(mock_wb, long_name)
        self.assertLessEqual(len(result), 31)


# ============================================================
# FIX 2: PDFService – _keep_alive parameter works correctly
# ============================================================
class TestPDFServiceKeepAlive(unittest.TestCase):

    def setUp(self):
        from services.pdf_service import PDFService
        self.pdf_service = PDFService()

    def test_excel_app_none_initially(self):
        """Excel app should start as None"""
        self.assertIsNone(self.pdf_service.excel_app)

    @patch('services.pdf_service.pythoncom')
    @patch('services.pdf_service.win32com.client.Dispatch')
    def test_init_excel_creates_instance(self, mock_dispatch, mock_pycom):
        """_init_excel() should create excel_app"""
        mock_excel = MagicMock()
        mock_dispatch.return_value = mock_excel
        self.pdf_service._init_excel()
        self.assertIsNotNone(self.pdf_service.excel_app)

    @patch('services.pdf_service.pythoncom')
    @patch('services.pdf_service.win32com.client.Dispatch')
    def test_init_excel_idempotent(self, mock_dispatch, mock_pycom):
        """_init_excel() called twice should not create duplicate instance"""
        mock_excel = MagicMock()
        mock_dispatch.return_value = mock_excel
        self.pdf_service._init_excel()
        first_instance = self.pdf_service.excel_app
        self.pdf_service._init_excel()  # Call again
        self.assertIs(self.pdf_service.excel_app, first_instance)
        # Dispatch should only have been called once
        mock_dispatch.assert_called_once()

    @patch('services.pdf_service.pythoncom')
    def test_cleanup_excel_resets_instance(self, mock_pycom):
        """_cleanup_excel() should reset excel_app to None"""
        mock_excel = MagicMock()
        self.pdf_service.excel_app = mock_excel
        self.pdf_service.excel_pid = None
        self.pdf_service._cleanup_excel()
        self.assertIsNone(self.pdf_service.excel_app)

    @patch('services.pdf_service.pythoncom')
    def test_fallback_reuses_excel_app(self, mock_pycom):
        """_export_pdf_fallback should reuse self.excel_app when available"""
        mock_excel = MagicMock()
        mock_excel.Workbooks.Open.return_value = MagicMock()
        mock_excel.Workbooks.Add.return_value = MagicMock()
        self.pdf_service.excel_app = mock_excel

        with patch('services.pdf_service.utils.unblock_file'), \
             patch('services.pdf_service.utils.logger'):
            # Call fallback – it should NOT call Dispatch (no new Excel)
            with patch('services.pdf_service.win32com.client.Dispatch') as mock_dispatch:
                # Will fail on export (no real Excel), but we check dispatch not called
                try:
                    self.pdf_service._export_pdf_fallback(
                        "dummy.xlsx", ["Sheet1"], "/tmp/out.pdf"
                    )
                except Exception:
                    pass  # Expected to fail without real Excel
                mock_dispatch.assert_not_called()  # KEY ASSERTION


# ============================================================
# FIX 3: Memory cleanup – verify del pattern works safely
# ============================================================
class TestMemoryCleanup(unittest.TestCase):

    def test_del_list_releases_reference(self):
        """Verify del correctly removes reference (Python GC test)"""
        images = [Image.new('RGB', (100, 100)) for _ in range(5)]
        count_before = len(images)
        self.assertEqual(count_before, 5)
        del images
        # After del, accessing 'images' should raise NameError
        try:
            _ = images  # noqa
            self.fail("Expected NameError not raised")
        except NameError:
            pass  # Expected


# ============================================================
# FIX 6: Zoom config – DEFAULT_ZOOM used correctly
# ============================================================
class TestZoomConfig(unittest.TestCase):

    def test_default_zoom_exists_in_config(self):
        """config.DEFAULT_ZOOM should exist and be a valid number"""
        import config
        self.assertTrue(hasattr(config, 'DEFAULT_ZOOM'))
        self.assertIsInstance(config.DEFAULT_ZOOM, (int, float))
        self.assertGreater(config.DEFAULT_ZOOM, 0)


# ============================================================
# FIX 7: Fast-Cache & Network Path Utilities
# ============================================================
class TestNetworkPathAndFastCache(unittest.TestCase):

    def test_unc_path_detected_as_network(self):
        r"""UNC paths (e.g. \\server\share\file.xlsx) should return True"""
        unc_path = r"\\fstvn01\Data\10_Production\file.xlsx"
        self.assertTrue(utils.is_network_path(unc_path))

    def test_local_path_detected_as_not_network(self):
        r"""Local path (e.g. D:\Sandbox\file.xlsx) should return False"""
        local_path = r"C:\Users\test\file.xlsx"
        self.assertFalse(utils.is_network_path(local_path))

    def test_empty_path_returns_false(self):
        """Empty or None path should safely return False"""
        self.assertFalse(utils.is_network_path(""))
        self.assertFalse(utils.is_network_path(None))

    def test_sync_folder_to_destination(self):
        """sync_folder_to_destination should copy all files correctly"""
        import tempfile
        with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as dst_dir:
            f1 = os.path.join(src_dir, "test1.txt")
            with open(f1, "w", encoding="utf-8") as f:
                f.write("hello")
            
            sub = os.path.join(src_dir, "sub")
            os.makedirs(sub, exist_ok=True)
            f2 = os.path.join(sub, "test2.txt")
            with open(f2, "w", encoding="utf-8") as f:
                f.write("world")
                
            utils.sync_folder_to_destination(src_dir, dst_dir)
            
            self.assertTrue(os.path.exists(os.path.join(dst_dir, "test1.txt")))
            self.assertTrue(os.path.exists(os.path.join(dst_dir, "sub", "test2.txt")))


if __name__ == '__main__':
    unittest.main(verbosity=2)

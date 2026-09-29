import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from PIL import Image, ImageDraw

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.comparator import Comparator
from services.optimized_image_compare import (
    compare_images_opencv, compare_images_pil, quick_compare_hash, create_side_by_side
)

class TestComparator(unittest.TestCase):

    def setUp(self):
        self.comparator = Comparator()

    def test_comparator_initialization(self):
        """Test that Comparator initializes correctly and has expected attributes"""
        self.assertIsNotNone(self.comparator)
        self.assertIsNotNone(self.comparator.pdf_service)
        self.assertFalse(self.comparator.use_pdf_method)

    def test_compare_images_identical_no_diff(self):
        """Test comparing identical images reports has_diff = False"""
        img1 = Image.new('RGB', (200, 200), color=(255, 255, 255))
        img2 = Image.new('RGB', (200, 200), color=(255, 255, 255))
        
        left, right, has_diff, diff_pixels = compare_images_opencv(img1, img2, diff_threshold=25)
        self.assertFalse(has_diff)
        self.assertEqual(diff_pixels, 0)

    def test_compare_images_different_reports_diff(self):
        """Test comparing different images reports has_diff = True with pixel count"""
        img1 = Image.new('RGB', (200, 200), color=(255, 255, 255))
        img2 = Image.new('RGB', (200, 200), color=(255, 255, 255))
        
        # Draw a black box on img1
        draw = ImageDraw.Draw(img1)
        draw.rectangle([50, 50, 80, 80], fill=(0, 0, 0))
        
        left, right, has_diff, diff_pixels = compare_images_opencv(img1, img2, diff_threshold=25)
        self.assertTrue(has_diff)
        self.assertGreater(diff_pixels, 0)

    def test_compare_images_pil_fallback(self):
        """Test PIL fallback comparison logic"""
        img1 = Image.new('RGB', (100, 100), color=(240, 240, 240))
        img2 = Image.new('RGB', (100, 100), color=(240, 240, 240))
        
        left, right, has_diff, diff_pixels = compare_images_pil(img1, img2, diff_threshold=25)
        self.assertFalse(has_diff)
        
        # Modify img1
        draw = ImageDraw.Draw(img1)
        draw.rectangle([10, 10, 30, 30], fill=(0, 0, 0))
        
        left2, right2, has_diff2, diff_pixels2 = compare_images_pil(img1, img2, diff_threshold=25)
        self.assertTrue(has_diff2)

    def test_create_side_by_side(self):
        """Test side by side image creation"""
        img1 = Image.new('RGB', (100, 150), color=(255, 0, 0))
        img2 = Image.new('RGB', (100, 150), color=(0, 255, 0))
        
        side = create_side_by_side(img1, img2)
        self.assertEqual(side.width, 200)
        self.assertEqual(side.height, 150)

    def test_jitter_tolerance_one_pixel_shift(self):
        """Test that 1-pixel line shift is tolerated without false positive"""
        # Vertical line shifted by 1 pixel
        img1 = Image.new('RGB', (100, 100), color=(255, 255, 255))
        d1 = ImageDraw.Draw(img1)
        d1.line([(50, 10), (50, 90)], fill=(0, 0, 0), width=1)

        img2 = Image.new('RGB', (100, 100), color=(255, 255, 255))
        d2 = ImageDraw.Draw(img2)
        d2.line([(51, 10), (51, 90)], fill=(0, 0, 0), width=1)

        left, right, has_diff, diff_pixels = compare_images_opencv(img1, img2, diff_threshold=40)
        self.assertFalse(has_diff)
        self.assertEqual(diff_pixels, 0)

        # Horizontal line shifted by 1 pixel
        img3 = Image.new('RGB', (100, 100), color=(255, 255, 255))
        d3 = ImageDraw.Draw(img3)
        d3.line([(10, 50), (90, 50)], fill=(0, 0, 0), width=1)

        img4 = Image.new('RGB', (100, 100), color=(255, 255, 255))
        d4 = ImageDraw.Draw(img4)
        d4.line([(10, 51), (90, 51)], fill=(0, 0, 0), width=1)

        left2, right2, has_diff2, diff_pixels2 = compare_images_opencv(img3, img4, diff_threshold=40)
        self.assertFalse(has_diff2)
        self.assertEqual(diff_pixels2, 0)

    def test_jitter_tolerance_two_pixel_shift_detected(self):
        """Test that true shifts (>= 2 pixels) are detected as differences"""
        img1 = Image.new('RGB', (100, 100), color=(255, 255, 255))
        d1 = ImageDraw.Draw(img1)
        d1.line([(50, 10), (50, 90)], fill=(0, 0, 0), width=1)

        img2 = Image.new('RGB', (100, 100), color=(255, 255, 255))
        d2 = ImageDraw.Draw(img2)
        d2.line([(52, 10), (52, 90)], fill=(0, 0, 0), width=1)

        left, right, has_diff, diff_pixels = compare_images_opencv(img1, img2, diff_threshold=40)
        self.assertTrue(has_diff)
        self.assertGreater(diff_pixels, 0)

    def test_jitter_tolerance_line_addition_and_deletion(self):
        """Test that added or deleted lines are detected even if 1-pixel wide"""
        blank = Image.new('RGB', (100, 100), color=(255, 255, 255))
        with_line = Image.new('RGB', (100, 100), color=(255, 255, 255))
        d = ImageDraw.Draw(with_line)
        d.line([(50, 10), (50, 90)], fill=(0, 0, 0), width=1)

        # Added line (new has line, old is blank)
        left, right, has_diff, diff_pixels = compare_images_opencv(with_line, blank, diff_threshold=40)
        self.assertTrue(has_diff)
        self.assertGreater(diff_pixels, 0)

        # Deleted line (new is blank, old has line)
        left2, right2, has_diff2, diff_pixels2 = compare_images_opencv(blank, with_line, diff_threshold=40)
        self.assertTrue(has_diff2)
        self.assertGreater(diff_pixels2, 0)

    def test_apply_sheet_layout_handles_none_current_layout(self):
        """Test that _apply_sheet_layout gracefully handles None for current_layout without crashing"""
        from services.pdf_service import PDFService
        from unittest.mock import MagicMock

        mock_sheet = MagicMock()
        mock_sheet.Columns.return_value = MagicMock()
        mock_sheet.Rows.return_value = MagicMock()

        layout = {
            "columns": [{"index": 1, "size": 10.0, "hidden": False}],
            "rows": [{"index": 1, "size": 20.0, "hidden": False}],
        }
        # Should not raise TypeError: 'NoneType' object is not iterable
        PDFService._apply_sheet_layout(mock_sheet, layout, current_layout=None)

    def test_pagesetup_margins_normalized_to_zero(self):
        """Test that PageSetup margins are normalized to 0 in export_sheets_to_pdf"""
        from services.pdf_service import PDFService
        from unittest.mock import MagicMock, patch

        pdf_service = PDFService()
        pdf_service.excel_app = MagicMock()

        mock_wb = MagicMock()
        pdf_service.excel_app.Workbooks.Open.return_value = mock_wb

        mock_sheet = MagicMock()
        mock_sheet.Name = "Sheet1"
        mock_wb.Sheets = [mock_sheet]
        mock_wb.Worksheets = [mock_sheet]

        mock_ps = MagicMock()
        mock_sheet.PageSetup = mock_ps

        with patch.object(pdf_service, '_find_sheet', return_value=mock_sheet):
            with patch('os.path.exists', return_value=True):
                pdf_service.export_sheets_to_pdf("dummy.xlsx", ["Sheet1"], "dummy.pdf")

        self.assertEqual(mock_ps.LeftMargin, 0)
        self.assertEqual(mock_ps.RightMargin, 0)
        self.assertEqual(mock_ps.TopMargin, 0)
        self.assertEqual(mock_ps.BottomMargin, 0)

    def test_brightness_increase_40_percent_no_diff(self):
        """Test that pure +40% brightness and -40% contrast is normalized without false positive diff"""
        import numpy as np
        # Create a textured raster image with varied intensity levels
        arr = np.zeros((120, 150, 3), dtype=np.uint8)
        for i in range(120):
            for j in range(150):
                arr[i, j] = [(i * 2) % 200 + 30, (j * 2) % 200 + 30, ((i + j)) % 200 + 30]
        
        img_orig = Image.fromarray(arr)
        # Apply Excel-like Brightness +40%, Contrast -40%
        arr_bright = np.clip(0.6 * arr.astype(float) + 0.4 * 255, 0, 255).astype(np.uint8)
        img_bright = Image.fromarray(arr_bright)

        left, right, has_diff, diff_pixels = compare_images_opencv(img_bright, img_orig, diff_threshold=40)
        self.assertFalse(has_diff, f"Pure brightness +40% should not be marked as diff, got diff_pixels={diff_pixels}")
        self.assertEqual(diff_pixels, 0)

    def test_brightness_decrease_40_percent_no_diff(self):
        """Test that pure -40% brightness is normalized without false positive diff"""
        import numpy as np
        arr = np.zeros((120, 150, 3), dtype=np.uint8)
        for i in range(120):
            for j in range(150):
                arr[i, j] = [(i * 2) % 180 + 50, (j * 2) % 180 + 50, ((i + j)) % 180 + 50]
        
        img_orig = Image.fromarray(arr)
        # Apply Brightness -40%
        arr_dark = np.clip(0.6 * arr.astype(float), 0, 255).astype(np.uint8)
        img_dark = Image.fromarray(arr_dark)

        left, right, has_diff, diff_pixels = compare_images_opencv(img_dark, img_orig, diff_threshold=40)
        self.assertFalse(has_diff, f"Pure brightness -40% should not be marked as diff, got diff_pixels={diff_pixels}")
        self.assertEqual(diff_pixels, 0)

    def test_brightness_increase_with_added_element_detected(self):
        """Test that real modifications (added arrow/line) on brightened images are still detected"""
        import numpy as np
        arr = np.zeros((120, 150, 3), dtype=np.uint8)
        for i in range(120):
            for j in range(150):
                arr[i, j] = [(i * 2) % 200 + 30, (j * 2) % 200 + 30, ((i + j)) % 200 + 30]
        
        img_orig = Image.fromarray(arr)
        arr_bright = np.clip(0.6 * arr.astype(float) + 0.4 * 255, 0, 255).astype(np.uint8)
        img_bright_mod = Image.fromarray(arr_bright)
        
        # Add a prominent red arrow/line on the brightened image
        d = ImageDraw.Draw(img_bright_mod)
        d.line([(30, 60), (100, 60)], fill=(255, 0, 0), width=3)
        d.polygon([(100, 55), (115, 60), (100, 65)], fill=(255, 0, 0))

        left, right, has_diff, diff_pixels = compare_images_opencv(img_bright_mod, img_orig, diff_threshold=40)
        self.assertTrue(has_diff, "Added arrow/line on brightened image must be detected")
        self.assertGreater(diff_pixels, 30)

    def test_brightness_increase_with_changed_text_detected(self):
        """Test that text modifications on brightened images are detected"""
        import numpy as np
        arr = np.full((80, 200, 3), 200, dtype=np.uint8)
        for i in range(80):
            arr[i, :] = [180 + i // 4, 180 + i // 4, 180 + i // 4]
        
        img_orig = Image.fromarray(arr)
        d_orig = ImageDraw.Draw(img_orig)
        d_orig.text((20, 30), "PART-001", fill=(0, 0, 0))
        
        # Brighten base and change text to PART-002
        arr_bright = np.clip(0.6 * np.array(img_orig).astype(float) + 0.4 * 255, 0, 255).astype(np.uint8)
        img_bright = Image.fromarray(arr_bright)
        # Erase old text area and write new text
        d_new = ImageDraw.Draw(img_bright)
        d_new.rectangle([80, 25, 120, 50], fill=(240, 240, 240))
        d_new.text((20, 30), "PART-002", fill=(0, 0, 0))

        left, right, has_diff, diff_pixels = compare_images_opencv(img_bright, img_orig, diff_threshold=40)
        self.assertTrue(has_diff, "Text change from PART-001 to PART-002 must be detected")
        self.assertGreater(diff_pixels, 0)

    def test_deleted_component_not_masked_as_brightness_diff(self):
        """Test that deleting a dark component (100x100) is detected and NOT falsely masked as brightness shift"""
        import numpy as np
        old_arr = np.zeros((200, 200, 3), dtype=np.uint8)
        old_arr[50:150, 50:150] = 30
        old_arr[50:150:2, 50:150:2] = 45
        img_old = Image.fromarray(old_arr)

        new_arr = old_arr.copy()
        new_arr[50:150, 50:150] = 255
        img_new = Image.fromarray(new_arr)

        left, right, has_diff, diff_pixels = compare_images_opencv(img_new, img_old, diff_threshold=40)
        self.assertTrue(has_diff, "Deleted dark component must be detected")
        self.assertGreater(diff_pixels, 5000)

    def test_whited_out_patch_on_textured_image_detected(self):
        """Test that whiting out a 20x20 patch on a textured image is detected"""
        import numpy as np
        arr = np.zeros((120, 150, 3), dtype=np.uint8)
        for i in range(120):
            for j in range(150):
                arr[i, j] = [(i * 2) % 200 + 30, (j * 2) % 200 + 30, ((i + j)) % 200 + 30]
        img_orig = Image.fromarray(arr)

        img_patch = img_orig.copy()
        d = ImageDraw.Draw(img_patch)
        d.rectangle([50, 40, 70, 60], fill=(255, 255, 255))

        left, right, has_diff, diff_pixels = compare_images_opencv(img_patch, img_orig, diff_threshold=40)
        self.assertTrue(has_diff, "Whited out patch must be detected")
        self.assertGreater(diff_pixels, 200)

    def test_deleted_grey_box_on_textured_background_detected(self):
        """Test that deleting a subtle grey element (170 -> 250) on background is detected"""
        import numpy as np
        old_arr = np.full((100, 100, 3), 200, dtype=np.uint8)
        old_arr[30:70, 30:70] = [170, 170, 170]
        old_arr[::2, ::2] += 10
        img_old = Image.fromarray(old_arr)

        new_arr = old_arr.copy()
        new_arr[30:70, 30:70] = [250, 250, 250]
        img_new = Image.fromarray(new_arr)

        left, right, has_diff, diff_pixels = compare_images_opencv(img_new, img_old, diff_threshold=40)
        self.assertTrue(has_diff, "Deleted grey box must be detected")
        self.assertGreater(diff_pixels, 500)

    def test_smart_name_prefix_extracts_id_when_new_is_generic(self):
        """Test that generic new template filename gets old document code prepended"""
        from services.report_service import ReportService
        f_new = "KDTVN-A-PE-BM-014-X Bản yêu cầu đối ứng khẩn cấp New_2026.xlsm"
        f_old = "VN 36223.xlsm"
        prefix = ReportService.get_smart_name_prefix(f_new, f_old)
        self.assertEqual(prefix, "[VN 36223] ")

    def test_smart_name_prefix_no_duplicate_when_already_in_new(self):
        """Test that if code is already in new filename, no prefix is added"""
        from services.report_service import ReportService
        f_new = "VN 35869 mới.xlsx"
        f_old = "VN 35869 cũ.xlsx"
        prefix = ReportService.get_smart_name_prefix(f_new, f_old)
        self.assertEqual(prefix, "")

    def test_smart_name_prefix_handles_none_or_empty(self):
        """Test graceful handling of None or empty paths"""
        from services.report_service import ReportService
        self.assertEqual(ReportService.get_smart_name_prefix("test.xlsx", None), "")
        self.assertEqual(ReportService.get_smart_name_prefix(None, "old.xlsx"), "")

    def test_smart_result_base_name_uses_code_for_generic_template(self):
        """Test that generic new template filename is replaced with concise [code]"""
        from services.report_service import ReportService
        f_new = "KDTVN-A-PE-BM-014-X Bản yêu cầu đối ứng khẩn cấp New_2026.xlsm"
        f_old = "VN 36223.xlsm"
        base = ReportService.get_smart_result_base_name(f_new, f_old)
        self.assertEqual(base, "[VN 36223]")

    def test_smart_result_base_name_keeps_normal_name(self):
        """Test that non-generic template filenames retain normal name"""
        from services.report_service import ReportService
        f_new = "VN 35869 mới.xlsx"
        f_old = "VN 35869 cũ.xlsx"
        base = ReportService.get_smart_result_base_name(f_new, f_old)
        self.assertEqual(base, "VN 35869 mới")

if __name__ == '__main__':
    unittest.main()



import os
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image, ImageDraw
import numpy as np
import fitz

from services.pdf_service import PDFService
from services.optimized_image_compare import compare_images_opencv, filter_thin_gridline_shifts, detect_thin_lines


class TestA4NormalizationAndGridlineFilter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scratch", "test_norm_unit")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.letter_pdf = os.path.join(self.temp_dir, "sample_letter.pdf")

        # Create a sample Letter-sized PDF (612 x 792 pt)
        doc = fitz.open()
        p = doc.new_page(width=612, height=792)
        p.draw_rect(fitz.Rect(50, 50, 562, 742), color=(0, 0, 0), width=1)
        p.insert_text((100, 100), "Letter Format Test", fontsize=16)
        doc.save(self.letter_pdf)
        doc.close()

    def tearDown(self):
        try:
            if os.path.exists(self.letter_pdf):
                os.remove(self.letter_pdf)
            for f in os.listdir(self.temp_dir):
                fp = os.path.join(self.temp_dir, f)
                if os.path.isfile(fp):
                    os.remove(fp)
            os.rmdir(self.temp_dir)
        except Exception:
            pass

    def test_normalize_pdf_to_a4_rescales_letter_to_a4(self):
        """Verify that normalize_pdf_to_a4 converts a US Letter PDF to standard A4 points."""
        success = PDFService.normalize_pdf_to_a4(self.letter_pdf)
        self.assertTrue(success)

        doc = fitz.open(self.letter_pdf)
        page = doc[0]
        # Standard A4: 595.28 x 841.89 pt
        self.assertAlmostEqual(page.rect.width, 595.28, delta=1.0)
        self.assertAlmostEqual(page.rect.height, 841.89, delta=1.0)
        doc.close()

    def test_render_pdf_to_images_normalizes_letter_to_a4_pixel_resolution(self):
        """Verify that render_pdf_to_images produces 827x1170 px images for Letter PDF at 100 DPI."""
        service = PDFService()
        images = service.render_pdf_to_images(self.letter_pdf, dpi=100)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0].size, (827, 1170))

    def test_render_pdf_page_normalizes_letter_to_a4_pixel_resolution(self):
        """Verify that render_pdf_page produces 827x1170 px image for Letter PDF at 100 DPI."""
        service = PDFService()
        img = service.render_pdf_page(self.letter_pdf, page_num=0, dpi=100)
        self.assertIsNotNone(img)
        self.assertEqual(img.size, (827, 1170))

    def test_ensure_a4_printer_sets_microsoft_print_to_pdf(self):
        """Verify that _ensure_a4_printer sets ActivePrinter to Microsoft Print to PDF."""
        mock_app = MagicMock()
        mock_app.ActivePrinter = "Kyocera CS 4053ci on Ne26:"

        result = PDFService._ensure_a4_printer(mock_app)
        self.assertTrue(result)
        self.assertIn("Microsoft Print to PDF", str(mock_app.ActivePrinter))

    def test_sync_changed_layout_uses_float_row_height_from_xml(self):
        """Verify that _sync_changed_layout_from_com assigns exact XML float RowHeight (e.g. 17.15)."""
        mock_target_sheet = MagicMock()
        mock_ref_sheet = MagicMock()

        # Simulate reference layout with exact float height 17.15 from openpyxl
        reference_layout = {
            "columns": [{"index": 1, "size": 10.0, "hidden": False}],
            "rows": [{"index": 1, "size": 17.15, "hidden": False}],
        }
        # Current layout in destination has default height 15.0
        current_layout = {
            "columns": [{"index": 1, "size": 10.0, "hidden": False}],
            "rows": [{"index": 1, "size": 15.0, "hidden": False}],
        }

        PDFService._sync_changed_layout_from_com(
            target_sheet=mock_target_sheet,
            reference_sheet=mock_ref_sheet,
            reference_layout=reference_layout,
            current_layout=current_layout,
            print_area="A1:A1",
        )

        mock_target_sheet.Range.assert_called_with("1:1")
        # Ensure exact float 17.15 was assigned, not integer 17 or COM getter
        self.assertEqual(mock_target_sheet.Range("1:1").EntireRow.RowHeight, 17.15)

    def test_filter_thin_gridline_shifts_eliminates_subpixel_1px_shift(self):
        """Verify that 1px line shift present in both images is eliminated by gridline filter."""
        im1 = Image.new("RGB", (120, 120), (255, 255, 255))
        d1 = ImageDraw.Draw(im1)
        d1.line([(10, 60), (110, 60)], fill=(0, 0, 0), width=1)
        d1.line([(60, 10), (60, 110)], fill=(0, 0, 0), width=1)

        # 1px shift horizontally and vertically
        im2 = Image.new("RGB", (120, 120), (255, 255, 255))
        d2 = ImageDraw.Draw(im2)
        d2.line([(10, 61), (110, 61)], fill=(0, 0, 0), width=1)
        d2.line([(61, 10), (61, 110)], fill=(0, 0, 0), width=1)

        left, right, has_diff, diff_pixels = compare_images_opencv(im1, im2, diff_threshold=40)
        self.assertFalse(has_diff, f"1px line shift should be filtered, got diff_pixels={diff_pixels}")
        self.assertEqual(diff_pixels, 0)

    def test_filter_thin_gridline_shifts_preserves_added_line(self):
        """Verify that genuinely added gridlines are detected as diff."""
        blank = Image.new("RGB", (100, 100), (255, 255, 255))
        with_line = Image.new("RGB", (100, 100), (255, 255, 255))
        ImageDraw.Draw(with_line).line([(10, 50), (90, 50)], fill=(0, 0, 0), width=1)

        left, right, has_diff, diff_pixels = compare_images_opencv(with_line, blank, diff_threshold=40)
        self.assertTrue(has_diff, "Added line must be detected")
        self.assertGreater(diff_pixels, 0)

    def test_filter_thin_gridline_shifts_preserves_text_change_near_line(self):
        """Verify that text changes near table lines are preserved and detected."""
        im1 = Image.new("RGB", (200, 100), (255, 255, 255))
        d1 = ImageDraw.Draw(im1)
        d1.line([(10, 50), (190, 50)], fill=(0, 0, 0), width=1)
        d1.text((30, 30), "CODE-A", fill=(0, 0, 0))

        im2 = Image.new("RGB", (200, 100), (255, 255, 255))
        d2 = ImageDraw.Draw(im2)
        # Shift line by 1px AND change text to CODE-B
        d2.line([(10, 51), (190, 51)], fill=(0, 0, 0), width=1)
        d2.text((30, 30), "CODE-B", fill=(0, 0, 0))

        left, right, has_diff, diff_pixels = compare_images_opencv(im1, im2, diff_threshold=40)
        self.assertTrue(has_diff, "Text change near line must be detected")
        self.assertGreater(diff_pixels, 0)

    def test_normalize_pdf_to_a4_preserves_content_origin_without_vertical_shift(self):
        """Verify that normalize_pdf_to_a4 scales content directly to (0, 0) without 35pt letterbox margin."""
        test_pdf = os.path.join(self.temp_dir, "content_origin_test.pdf")
        doc = fitz.open()
        p = doc.new_page(width=612, height=792)
        # Top border at y=10
        p.draw_rect(fitz.Rect(10, 10, 602, 782), color=(0, 0, 0), width=1)
        doc.save(test_pdf)
        doc.close()

        PDFService.normalize_pdf_to_a4(test_pdf)

        doc_norm = fitz.open(test_pdf)
        pix = doc_norm[0].get_pixmap()
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, 3))
        black_y = np.where(arr[:, :, 0] < 50)[0]
        # In unletterboxed scaling: y=10 * (841.89 / 792.0) = 10.63 -> pix index 10-12
        # If letterboxed, black_y.min() would be ~45
        self.assertLess(black_y.min(), 15, f"Content was shifted down by letterboxing, top pixel at {black_y.min()}")
        doc_norm.close()

    def test_detect_thin_lines_identifies_antialiased_and_multi_pixel_lines(self):
        """Verify that detect_thin_lines identifies antialiased lines split across 2 subpixel rows."""
        # Antialiased line: 50% split across rows 20 and 21
        gray_aa = np.full((50, 60), 255, dtype=np.uint8)
        gray_aa[20, :] = 110
        gray_aa[21, :] = 110
        res_aa = detect_thin_lines(gray_aa, is_horizontal=True)
        detected_rows = np.where(res_aa.any(axis=1))[0]
        self.assertTrue(20 in detected_rows or 21 in detected_rows, "Antialiased 2px line must be detected")

        # 2px dark line
        gray_2px = np.full((50, 60), 255, dtype=np.uint8)
        gray_2px[20:22, :] = 0
        res_2px = detect_thin_lines(gray_2px, is_horizontal=True)
        detected_2px_rows = np.where(res_2px.any(axis=1))[0]
        self.assertTrue(20 in detected_2px_rows or 21 in detected_2px_rows, "2px dark line must be detected")

    def test_filter_thin_gridline_shifts_eliminates_antialiased_subpixel_shift(self):
        """Verify that subpixel line shift with antialiasing (simulating 0.05pt row diff) is eliminated."""
        im1 = np.full((60, 100, 3), 255, dtype=np.uint8)
        im1[20, 10:90, :] = 120
        im1[21, 10:90, :] = 130

        im2 = np.full((60, 100, 3), 255, dtype=np.uint8)
        im2[21, 10:90, :] = 50

        pil1 = Image.fromarray(im1)
        pil2 = Image.fromarray(im2)

        left, right, has_diff, diff_pixels = compare_images_opencv(pil1, pil2, diff_threshold=40)
        self.assertFalse(has_diff, f"Antialiased 1.5-2px line shift should be filtered, got diff_pixels={diff_pixels}")
        self.assertEqual(diff_pixels, 0)


if __name__ == "__main__":
    unittest.main()

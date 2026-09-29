import os
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image
import numpy as np
import fitz

from services.pdf_service import PDFService
from services.optimized_image_compare import compare_images_opencv


class TestA4Normalization(unittest.TestCase):
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
        self.assertLess(black_y.min(), 15, f"Content was shifted down by letterboxing, top pixel at {black_y.min()}")
        doc_norm.close()


if __name__ == "__main__":
    unittest.main()

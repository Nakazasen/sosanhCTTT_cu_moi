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

if __name__ == '__main__':
    unittest.main()

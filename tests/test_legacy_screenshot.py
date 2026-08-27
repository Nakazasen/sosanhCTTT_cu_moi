import unittest
from services.legacy_screenshot_service import LegacyScreenshotService
import config

class TestLegacyScreenshotService(unittest.TestCase):
    def setUp(self):
        self.service = LegacyScreenshotService()

    def test_default_goto_address_is_ex1(self):
        self.assertEqual(self.service.goto_address, "EX1")

    def test_set_goto_address_alpha_normalization(self):
        self.service.set_goto_address("EX")
        self.assertEqual(self.service.goto_address, "EX1")
        self.service.set_goto_address("ex")
        self.assertEqual(self.service.goto_address, "EX1")

    def test_set_goto_address_fallback_for_a1_or_empty(self):
        self.service.set_goto_address("")
        self.assertEqual(self.service.goto_address, "EX1")
        self.service.set_goto_address("A1")
        self.assertEqual(self.service.goto_address, "EX1")
        self.service.set_goto_address("a1")
        self.assertEqual(self.service.goto_address, "EX1")

    def test_set_goto_address_custom(self):
        self.service.set_goto_address("EY5")
        self.assertEqual(self.service.goto_address, "EY5")

if __name__ == "__main__":
    unittest.main()

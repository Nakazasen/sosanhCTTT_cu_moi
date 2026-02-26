import unittest
import os
import sys
import shutil
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import utils

class TestPdfFixAndLogging(unittest.TestCase):

    def test_sanitize_filename_strict(self):
        """Test logic làm sạch tên file nghiêm ngặt"""
        # Case 1: Tên bình thường
        self.assertEqual(utils.sanitize_filename_strict("NormalName"), "NormalName")
        
        # Case 2: Ký tự đặc biệt Windows
        # < > : " / \ | ? *
        bad_name = 'File:Name/With<Special>Chars*"|?'
        expected = 'File_Name_With_Special_Chars____'
        self.assertEqual(utils.sanitize_filename_strict(bad_name), expected)
        
        # Case 3: Empty string
        self.assertEqual(utils.sanitize_filename_strict(""), "unnamed")
        
        # Case 4: Only special chars
        self.assertEqual(utils.sanitize_filename_strict("???"), "___")
        
        # Case 5: Control chars (\n, \t)
        self.assertEqual(utils.sanitize_filename_strict("Name\nWith\tTab"), "NameWithTab")

    def test_logging_setup(self):
        """Test initialization of hidden logging"""
        # Note: We can't fully test write permissions easily without side effects,
        # but we can check if the function returns a path or None, and doesn't crash.
        
        # Ensure we don't mess up global logging state too much, though basicConfig is idempotent-ish
        log_path = utils.setup_hidden_logging()
        
        self.assertIsNotNone(log_path)
        self.assertTrue(os.path.isabs(log_path))
        
        # Check if file was created (if we have permissions)
        if log_path and os.access(os.path.dirname(log_path), os.W_OK):
             # It might be created by the time we check, or on first log
             utils.logger.info("Test log entry")
             self.assertTrue(os.path.exists(log_path))

if __name__ == '__main__':
    unittest.main()

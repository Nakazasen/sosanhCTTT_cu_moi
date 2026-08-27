import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestFileSelectionLogic(unittest.TestCase):
    def test_deduplication_append(self):
        """Test that appending files preserves order and removes duplicates."""
        existing_files = [
            r"C:\data\file1.xlsx",
            r"C:\data\file2.xlsx",
        ]
        
        new_selected = [
            r"C:\data\file2.xlsx",  # duplicate
            r"C:\data\file3.xlsx",  # new
            r"C:\data\FILE1.XLSX",  # case-insensitive duplicate on Windows
        ]
        
        existing = {os.path.normcase(os.path.normpath(f)) for f in existing_files}
        for f in new_selected:
            norm = os.path.normcase(os.path.normpath(f))
            if norm not in existing:
                existing_files.append(f)
                existing.add(norm)
                
        self.assertEqual(len(existing_files), 3)
        self.assertEqual(existing_files[0], r"C:\data\file1.xlsx")
        self.assertEqual(existing_files[1], r"C:\data\file2.xlsx")
        self.assertEqual(existing_files[2], r"C:\data\file3.xlsx")


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.excel_service import ExcelService
import config

class TestExcelService(unittest.TestCase):

    def setUp(self):
        # Mock the Excel Application initialization
        with patch('win32com.client.Dispatch') as mock_dispatch:
            self.service = ExcelService(suppress_alerts=True)
            self.service.app = MagicMock()

    def test_make_unique_sheet_name(self):
        """Test logic tạo tên sheet duy nhất"""
        # Mock workbook
        mock_wb = MagicMock()
        
        # Case 1: Tên chưa tồn tại
        mock_sheet1 = MagicMock()
        mock_sheet1.Name = "Sheet1"
        mock_wb.Sheets = [mock_sheet1]
        
        result = self.service._make_unique_sheet_name(mock_wb, "NewSheet")
        self.assertEqual(result, "NewSheet")

        # Case 2: Tên đã tồn tại
        mock_sheet2 = MagicMock()
        mock_sheet2.Name = "NewSheet"
        mock_wb.Sheets = [mock_sheet1, mock_sheet2]
        
        result = self.service._make_unique_sheet_name(mock_wb, "NewSheet")
        self.assertEqual(result, "NewSheet_1")
        
        # Case 3: Tên trùng nhiều lần
        mock_sheet3 = MagicMock()
        mock_sheet3.Name = "NewSheet_1"
        mock_wb.Sheets = [mock_sheet1, mock_sheet2, mock_sheet3]
        
        result = self.service._make_unique_sheet_name(mock_wb, "NewSheet")
        self.assertEqual(result, "NewSheet_2")
        
        # Case 4: Tên quá dài (Excel limit 31 chars)
        long_name = "A_Very_Long_Sheet_Name_That_Exceeds_Thirty_One_Characters"
        result = self.service._make_unique_sheet_name(mock_wb, long_name)
        self.assertTrue(len(result) <= 31)
        self.assertEqual(result, long_name[:31])

    @patch('services.excel_service.utils')
    def test_standard_preprocess_green_tab_filter(self, mock_utils):
        """Test logic lọc sheet theo màu tab xanh"""
        # Setup mocks
        mock_wb = MagicMock()
        self.service.open_workbook = MagicMock(return_value=mock_wb)
        self.service.close_workbook = MagicMock()
        
        # Create sheets
        sheet_green = MagicMock()
        sheet_green.Name = "GreenSheet"
        sheet_green.Tab.Color = config.COLOR_GREEN_TAB # 5296274
        
        sheet_other = MagicMock()
        sheet_other.Name = "OtherSheet"
        sheet_other.Tab.Color = 123456 # Not green
        
        sheet_error = MagicMock()
        sheet_error.Name = "ErrorSheet"
        # Accessing Color raises exception
        type(sheet_error.Tab).Color = unittest.mock.PropertyMock(side_effect=Exception("No Color"))
        
        mock_wb.Sheets = [sheet_green, sheet_other, sheet_error]
        
        # Run preprocess
        self.service.standard_preprocess("dummy_path.xlsx")
        
        # Verify: Only GreenSheet should be renamed or touched
        # Check if Name property was set on GreenSheet (renamed/normalized)
        # "GreenSheet" -> "GreenSheet" (normalized)
        
        # To verify filter, we check which sheets had their properties accessed or modified
        # sheet_other should NOT have its Name modified (assignments)
        
        # Python mocks record calls. Let's see if we tried to set Name on sheets
        # sheet_green.Name = ... triggers a __setattr__ call essentially, or set property
        
        # In the code: 
        # sheet.Name = unique_name (only if new_name != original_name)
        # But "GreenSheet" normalized is "GreenSheet". It won't be renamed unless special chars.
        
        # Let's retry with a name needing normalization to verify it processed
        sheet_green.Name = "Green_Sheet" # Should become "Green-Sheet"
        sheet_other.Name = "Other_Sheet" # Should remain "Other_Sheet"
        
        self.service.standard_preprocess("dummy_path.xlsx")
        
        # Green Sheet should be renamed
        self.assertEqual(sheet_green.Name, "Green-Sheet")
        
        # Other Sheet should NOT be renamed (Name assignment not called)
        self.assertEqual(sheet_other.Name, "Other_Sheet")

    @patch('services.excel_service.utils')
    def test_standard_preprocess_old_file_auto_b(self, mock_utils):
        """Test logic tiền xử lý file cũ và đồng bộ auto_add_b"""
        mock_wb = MagicMock()
        self.service.open_workbook = MagicMock(return_value=mock_wb)
        self.service.close_workbook = MagicMock()
        
        sheet_old1 = MagicMock()
        sheet_old1.Name = "01-CTTT"
        sheet_old1.Tab.Color = 0 # Not green
        
        sheet_old2 = MagicMock()
        sheet_old2.Name = "OtherSheet"
        sheet_old2.Tab.Color = 0
        
        mock_wb.Sheets = [sheet_old1, sheet_old2]
        
        # Reference new sheets where 01-CTTT has 'b' -> "b01-CTTT"
        ref_new_sheets = [("01-CTTT", "b01-CTTT")]
        
        self.service.standard_preprocess("dummy_old.xlsx", is_new=False, auto_add_b=True, new_sheet_names_ref=ref_new_sheets)
        
        # sheet_old1 should be renamed to "b01-CTTT"
        self.assertEqual(sheet_old1.Name, "b01-CTTT")
        # sheet_old2 should remain "OtherSheet"
        self.assertEqual(sheet_old2.Name, "OtherSheet")

if __name__ == '__main__':
    unittest.main()

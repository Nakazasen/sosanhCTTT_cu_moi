import win32com.client
import pythoncom
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"\\fstvn01\Data\00_KDTVN Common(KDTVN共通)\⑤Production Engineering(製造技術)\Hang muc can luu\Vinh\sosanhDUKC_CTTT\【緊急対応添付資料】3V2RV00280_EXIT_ASSY_23.01.2025_1 Mới.xls"

pythoncom.CoInitialize()
excel = win32com.client.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

wb = excel.Workbooks.Open(file_path, ReadOnly=True)

for sheet in wb.Sheets:
    if sheet.Visible == -1:
        ps = sheet.PageSetup
        print(f"=== Sheet: {sheet.Name} ===")
        print(f"  PrintArea (Original): {ps.PrintArea}")
        print(f"  Orientation: {ps.Orientation} (1=Portrait, 2=Landscape)")
        print(f"  PaperSize: {ps.PaperSize} (9=A4)")
        print(f"  Zoom: {ps.Zoom}")
        print(f"  FitToPagesWide: {ps.FitToPagesWide}")
        print(f"  FitToPagesTall: {ps.FitToPagesTall}")
        print(f"  UsedRange: {sheet.UsedRange.Address}")

wb.Close(SaveChanges=False)
excel.Quit()
pythoncom.CoUninitialize()

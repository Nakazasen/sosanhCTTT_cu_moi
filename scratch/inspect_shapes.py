import win32com.client
import pythoncom
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

sample_dir = r"\\fstvn01\Data\00_KDTVN Common(KDTVN共通)\⑤Production Engineering(製造技術)\Hang muc can luu\Vinh\sosanhDUKC_CTTT"
fpath = os.path.join(sample_dir, "【緊急対応添付資料】3V2RV00280_EXIT_ASSY_23.01.2025_1 Mới.xls")

pythoncom.CoInitialize()
excel = win32com.client.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

wb = excel.Workbooks.Open(fpath, ReadOnly=True)

for sheet in wb.Sheets:
    if sheet.Visible == -1 and sheet.Name != "Sheet1":
        print(f"\n=== Sheet: {sheet.Name} ===")
        # Check shapes / pictures
        print(f"  Shape count: {sheet.Shapes.Count}")
        for i, shape in enumerate(sheet.Shapes, 1):
            if i <= 10:
                print(f"    Shape {i}: name='{shape.Name}', type={shape.Type}, left={shape.Left}, top={shape.Top}, width={shape.Width}, height={shape.Height}")
        # Check cells with values
        print(f"  J2: {sheet.Range('J2').Value}")
        print(f"  BD76: {sheet.Range('BD76').Value}")
        print(f"  A1: {sheet.Range('A1').Value}")

wb.Close(SaveChanges=False)
excel.Quit()
pythoncom.CoUninitialize()

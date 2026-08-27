import win32com.client
import pythoncom
import os
import sys
import fitz  # PyMuPDF

sys.stdout.reconfigure(encoding='utf-8')

sample_dir = r"\\fstvn01\Data\00_KDTVN Common(KDTVN共通)\⑤Production Engineering(製造技術)\Hang muc can luu\Vinh\sosanhDUKC_CTTT"
fpath = os.path.join(sample_dir, "【緊急対応添付資料】3V2RV00280_EXIT_ASSY_23.01.2025_1 Mới.xls")
out_pdf = os.path.join(os.path.dirname(__file__), "test_paging_output.pdf")

pythoncom.CoInitialize()
excel = win32com.client.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

wb = excel.Workbooks.Open(fpath, ReadOnly=True)

# Test on sheet 変更後004 and 変更後COVER
for sname in ["変更後COVER", "変更後004", "変更後005"]:
    sheet = wb.Sheets(sname)
    sheet.Activate()
    ps = sheet.PageSetup
    ps.PrintArea = "J2:BD76"
    ps.Zoom = False
    ps.FitToPagesWide = 1
    ps.FitToPagesTall = False  # Allow multi-page splitting!
    ps.CenterHorizontally = True
    print(f"Sheet {sname} setup done: PrintArea={ps.PrintArea}, Zoom={ps.Zoom}, FitWide={ps.FitToPagesWide}, FitTall={ps.FitToPagesTall}")

# Export sheet 変更後004 to PDF
temp_pdf = os.path.join(os.path.dirname(__file__), "test_004.pdf")
wb.Sheets("変更後004").ExportAsFixedFormat(0, temp_pdf, 0, True, False)

wb.Close(SaveChanges=False)
excel.Quit()
pythoncom.CoUninitialize()

# Inspect generated PDF
doc = fitz.open(temp_pdf)
print(f"\nGenerated PDF page count: {len(doc)}")
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=100)
    print(f"  Page {i+1}: size={pix.width}x{pix.height} px, rect={page.rect}")
    # save preview image
    pix.save(os.path.join(os.path.dirname(__file__), f"preview_page_{i+1}.png"))
doc.close()

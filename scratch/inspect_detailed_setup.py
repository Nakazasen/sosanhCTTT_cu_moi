import win32com.client
import pythoncom
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

sample_dir = r"\\fstvn01\Data\00_KDTVN Common(KDTVN共通)\⑤Production Engineering(製造技術)\Hang muc can luu\Vinh\sosanhDUKC_CTTT"

pythoncom.CoInitialize()
excel = win32com.client.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

for fname in ["【緊急対応添付資料】3V2RV00280_EXIT_ASSY_23.01.2025_1 Mới.xls", "DUKC mới.xlsm"]:
    fpath = os.path.join(sample_dir, fname)
    wb = excel.Workbooks.Open(fpath, ReadOnly=True)
    print(f"=== File: {fname} ===")
    for s in wb.Sheets:
        if s.Visible == -1:
            ps = s.PageSetup
            print(f"  Sheet: {s.Name}")
            print(f"    Orientation: {ps.Orientation} (1=xlPortrait, 2=xlLandscape)")
            print(f"    PaperSize: {ps.PaperSize} (9=xlPaperA4, 8=xlPaperA3)")
            print(f"    Zoom: {ps.Zoom}")
            print(f"    FitToPagesWide: {ps.FitToPagesWide}, FitToPagesTall: {ps.FitToPagesTall}")
            print(f"    HPageBreaks: {s.HPageBreaks.Count}, VPageBreaks: {s.VPageBreaks.Count}")
            print(f"    UsedRange: {s.UsedRange.Address}")
            # Check cell J2, BD76, A1, AT120
            try:
                print(f"    Range(J2:BD76) width/height: cols={s.Range('J2:BD76').Columns.Count}, rows={s.Range('J2:BD76').Rows.Count}")
            except:
                pass
    wb.Close(SaveChanges=False)

excel.Quit()
pythoncom.CoUninitialize()

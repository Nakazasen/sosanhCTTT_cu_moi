import os
import sys
import win32com.client
import pythoncom

sys.stdout.reconfigure(encoding='utf-8')

sample_dir = r'\\fstvn01\Data\00_KDTVN Common(KDTVN共通)\⑤Production Engineering(製造技術)\Hang muc can luu\Vinh\sosanhDUKC_CTTT'
pythoncom.CoInitialize()
excel = win32com.client.DispatchEx('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False

files = [
    'DUKC mới.xlsm', 'DUKC cũ.xlsm',
    '【緊急対応添付資料】3V2RV00280_EXIT_ASSY_23.01.2025_1 Mới.xls',
    '【緊急対応添付資料】3V2RV00280_EXIT_ASSY_23.01.2025_1 cũ.xls'
]

for fname in files:
    fpath = os.path.join(sample_dir, fname)
    print(f'=== {fname} ===')
    try:
        wb = excel.Workbooks.Open(fpath, ReadOnly=True)
        print(f'Sheet count: {wb.Sheets.Count}')
        for s in wb.Sheets:
            tab_color = getattr(s.Tab, 'Color', None)
            try:
                addr = s.UsedRange.Address
            except:
                addr = 'N/A'
            print(f'  Sheet: "{s.Name}", Visible: {s.Visible}, TabColor: {tab_color}, UsedRange: {addr}')
        wb.Close(SaveChanges=False)
    except Exception as e:
        print(f'Error opening {fname}: {e}')

excel.Quit()
pythoncom.CoUninitialize()

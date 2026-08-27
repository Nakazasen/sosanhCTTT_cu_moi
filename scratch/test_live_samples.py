import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.comparator import Comparator
import config

sys.stdout.reconfigure(encoding='utf-8')

sample_dir = r'\\fstvn01\Data\00_KDTVN Common(KDTVN共通)\⑤Production Engineering(製造技術)\Hang muc can luu\Vinh\sosanhDUKC_CTTT'
out_test_dir = os.path.join(sample_dir, f"KetQua_TestLive_{int(time.time())}")

print("=== TEST 1: So sánh Tờ phát hành ĐƯKC (DUKC mới vs DUKC cũ) ===")
comparator1 = Comparator(use_pdf_method=True)

new_dukc = os.path.join(sample_dir, "DUKC mới.xlsm")
old_dukc = os.path.join(sample_dir, "DUKC cũ.xlsm")

settings_dukc = {
    "doc_mode": config.DOC_MODE_DUKC_OTHER,
    "print_area": config.PRINT_AREA_DUKC_OTHER,
    "output_folder": out_test_dir,
    "dpi": 100,
    "pdf_diff_threshold": 40,
}

def log_cb(msg):
    print(f"  [Progress] {msg}")

elapsed1 = comparator1.start_comparison([new_dukc], [old_dukc], status_callback=log_cb, settings=settings_dukc)
print(f"Test 1 Finished in {elapsed1:.2f}s!")

print("\n=== TEST 2: So sánh CTTT Đính kèm ĐƯKC (Mới.xls vs cũ.xls) ===")
comparator2 = Comparator(use_pdf_method=True)
new_cttt = os.path.join(sample_dir, "【緊急対応添付資料】3V2RV00280_EXIT_ASSY_23.01.2025_1 Mới.xls")
old_cttt = os.path.join(sample_dir, "【緊急対応添付資料】3V2RV00280_EXIT_ASSY_23.01.2025_1 cũ.xls")

settings_cttt = {
    "doc_mode": config.DOC_MODE_DUKC_CTTT,
    "print_area": config.PRINT_AREA_DUKC_CTTT,
    "output_folder": out_test_dir,
    "dpi": 100,
    "pdf_diff_threshold": 40,
}

elapsed2 = comparator2.start_comparison([new_cttt], [old_cttt], status_callback=log_cb, settings=settings_cttt)
print(f"Test 2 Finished in {elapsed2:.2f}s!")

print("\n=== DANH SÁCH FILE KẾT QUẢ TẠI THƯ MỤC ĐÍCH ===")
print(f"Thư mục: {out_test_dir}")
if os.path.exists(out_test_dir):
    for root, dirs, files in os.walk(out_test_dir):
        for f in files:
            fp = os.path.join(root, f)
            print(f"  - {f} ({os.path.getsize(fp)} bytes)")
else:
    print("Thư mục chưa tồn tại!")

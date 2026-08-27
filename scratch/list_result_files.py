import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"\\fstvn01\Data\00_KDTVN Common(KDTVN共通)\⑤Production Engineering(製造技術)\Hang muc can luu\Vinh\sosanhDUKC_CTTT"

print(f"=== DANH SÁCH THƯ MỤC VÀ FILE KẾT QUẢ TẠI: {base_dir} ===")
for folder in sorted(os.listdir(base_dir)):
    full_p = os.path.join(base_dir, folder)
    if os.path.isdir(full_p):
        print(f"\n📂 Thư mục: {folder}")
        for item in sorted(os.listdir(full_p)):
            fpath = os.path.join(full_p, item)
            size_kb = os.path.getsize(fpath) / 1024
            print(f"   📄 {item} ({size_kb:.1f} KB)")

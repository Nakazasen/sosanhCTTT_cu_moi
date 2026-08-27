import os, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"\\fstvn01\Data\00_KDTVN Common(KDTVN共通)\⑤Production Engineering(製造技術)\Hang muc can luu\Vinh\sosanhDUKC_CTTT"
keep_folders = [
    "KetQuaSoSanh_CTTT_20260826_194817",
    "KetQuaSoSanh_CTTT_20260826_194901"
]
for item in os.listdir(base_dir):
    full_path = os.path.join(base_dir, item)
    if os.path.isdir(full_path) and item.startswith("KetQua"):
        if item not in keep_folders:
            try:
                shutil.rmtree(full_path)
                print(f"Deleted old folder: {item}")
            except Exception as e:
                print(f"Error deleting {item}: {e}")
print("Cleanup complete.")

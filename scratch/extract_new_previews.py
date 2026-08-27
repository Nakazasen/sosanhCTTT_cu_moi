import fitz
import os
import sys

pdf_path = r"\\fstvn01\Data\00_KDTVN Common(KDTVN共通)\⑤Production Engineering(製造技術)\Hang muc can luu\Vinh\sosanhDUKC_CTTT\KetQuaSoSanh_CTTT_20260826_194309\【緊急対応添付資料】3V2RV00280_EXIT_ASSY_23.01.2025_1 Mới.pdf"
out_img = r"C:\Users\tvn183660\.gemini\antigravity-ide\brain\fcf51e3e-d45d-4b67-968a-ab00956cde3e\scratch\preview_new_paging_p2.png"

doc = fitz.open(pdf_path)
print(f"Total pages in new PDF: {len(doc)}")
for i, p in enumerate(doc):
    pix = p.get_pixmap(dpi=150)
    img_save_path = r"C:\Users\tvn183660\.gemini\antigravity-ide\brain\fcf51e3e-d45d-4b67-968a-ab00956cde3e\scratch\preview_new_paging_p" + str(i+1) + ".png"
    pix.save(img_save_path)
    print(f"Saved page {i+1}: {pix.width}x{pix.height} to {img_save_path}")
doc.close()

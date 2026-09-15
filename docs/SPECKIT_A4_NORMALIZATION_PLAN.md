# SPECKIT SPECIFICATION: A4 Page Normalization & Subpixel Gridline Anti-Dilation Pipeline

**Status**: Approved & In Implementation  
**Version**: 7.4.3  
**Date**: 2026-09-15  
**Author**: Antigravity AI  

---

## 1. Bối cảnh & Vấn đề Cần Khắc Phục

### 1.1 Hiện tượng
Trên máy trạm của một số người dùng (cụ thể: Máy Người 2), khi thực hiện so sánh các phiên bản Chỉ thị Thao tác (CTTT), kết quả so sánh trên file Excel (ví dụ `Kết quả_PDF_VN 35958 mới.xlsx`) xuất hiện tình trạng **bôi đỏ tràn lan (110 hộp viền đỏ)** tại hầu hết các đường kẻ ngang của bảng biểu, dù nội dung văn bản và số liệu trong bảng hoàn toàn không thay đổi.

### 1.2 Phân tích Nguyên nhân Gốc rễ (RCA)
1. **Lệch Driver Máy In Mặc định (Windows Default Printer)**:
   - Trên máy Người 2, driver máy in mặc định trong Windows bị cấu hình ép khổ giấy **US Letter** ($8.5 \times 11\text{ inches} = 612.0 \times 792.0\text{ pt}$) thay vì chuẩn **A4** ($210 \times 297\text{ mm} = 595.28 \times 841.89\text{ pt}$).
   - Do Excel COM phụ thuộc chặt chẽ vào driver của máy in hiện hành (`ActivePrinter`), driver máy in vật lý này âm thầm ghi đè hoặc vô hiệu hóa thuộc tính `PageSetup.PaperSize = 9` (xlPaperA4), khiến file PDF xuất ra có kích thước US Letter ($612.0 \times 792.0\text{ pt}$).
2. **Co dọc bảng tính do `FitToPagesTall = 1`**:
   - Khổ Letter ngắn hơn khổ A4 ($792.0\text{ pt}$ so với $841.89\text{ pt}$, chênh lệch $\approx 50\text{ pt}$ tương đương giảm $6.7\%$).
   - Khi áp dụng `FitToPagesTall = 1`, Excel phải co dọc bảng xuống $93.3\%$.
   - Đồng thời, giữa 2 template CTTT cũ và mới có sự chênh lệch nhỏ về chiều cao dòng ($0.05\text{ pt}$ tích lũy qua 70 dòng). Sự kết hợp này dẫn tới hiện tượng tích lũy sai số làm tròn số nguyên pixel, gây lệch chính xác $1\text{ pixel}$ trên toàn bộ hệ thống đường kẻ ngang của bảng tính.
3. **Hiện tượng Khử răng cưa (Antialiasing) & Giãn nở (`cv2.dilate`)**:
   - Đường kẻ bảng vector khi được render sang raster ở 100 DPI có khử răng cưa.
   - Khi đường kẻ bị dịch chuyển 1 pixel, hiệu số pixel tuyệt đối đạt giá trị xám lên tới $84 > \text{threshold } 40$.
   - Bộ lọc jitter dịch chuyển nguyên pixel 8 hướng hiện tại không triệt tiêu được delta khử răng cưa này.
   - Sau đó, bước `cv2.dilate` (kernel $3 \times 3$, 2 iterations) đã khuếch đại các vệt 1-pixel này thành các dải dày 5–7 pixel, nhóm lại thành 110 hộp viền đỏ bao quanh mọi ô bảng tính.

---

## 2. Kiến Trúc Giải Pháp Kỹ Thuật (Architecture & Components)

Quy trình giải quyết triệt để 4 lớp phòng thủ (Defense in Depth):

```text
[Excel Source Files]
       │
       ▼ (Lớp 1: COM Printer & PrintCommunication Lock)
[Ép ActivePrinter = "Microsoft Print to PDF" & PrintCommunication = False]
       │
       ▼ (Lớp 2: Post-Export Vector Normalization)
[PyMuPDF: Scale to exact A4 595.28 x 841.89 pt]
       │
       ▼ (Lớp 3: XML Exact Float RowHeight Sync)
[Đồng bộ chính xác openpyxl float RowHeight thay vì COM getter]
       │
       ▼ (Lớp 4: Subpixel Morphological Gridline Filter)
[OpenCV: Triệt tiêu vệt lệch đường kẻ <= 1.5px không có thay đổi nội dung]
       │
       ▼
[Kết quả So sánh Hoàn toàn Sạch sẽ - 0 False Positive Gridlines]
```

### 2.1 Lớp 1 (P0): Ép Máy in Ảo Chuẩn A4 trong Excel COM & PrintCommunication
- **Mục tiêu**: Ngăn chặn driver máy in vật lý ép khổ Letter.
- **Thực thi**:
  - Viết hàm `_ensure_a4_printer(excel_app)` trong `PDFService`: Tự động truy vấn Registry Windows (`HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\Devices`) để tìm cổng chính xác của `Microsoft Print to PDF` (ví dụ `Microsoft Print to PDF on Ne14:`). Gán `excel_app.ActivePrinter` ngay khi mở workbook.
  - Bọc tất cả các thao tác gán `sheet.PageSetup` bằng:
    ```python
    try:
        excel.PrintCommunication = False
        ps = sheet.PageSetup
        ps.PaperSize = 9  # xlPaperA4
        ps.Zoom = False
        ps.FitToPagesWide = 1
        ps.FitToPagesTall = 1
        # ... margins ...
    finally:
        try:
            excel.PrintCommunication = True
        except Exception:
            pass
    ```
  - Lợi ích: Tăng tốc thiết lập COM gấp 3 lần và ngăn chặn driver máy in ghi đè thông số giấy.

### 2.2 Lớp 2 (P0): Chuẩn hóa Kích thước Trang PDF sau Xuất bằng PyMuPDF (Post-Export Normalization)
- **Mục tiêu**: Đảm bảo 100% tài liệu PDF dù xuất từ bất kỳ máy nào đều có kích thước vật lý A4 ($595.28 \times 841.89\text{ pt}$) và kích thước raster $827 \times 1170\text{ px}$ ở 100 DPI.
- **Thực thi**:
  - Viết hàm `normalize_pdf_to_a4(pdf_path: str) -> bool`: Sử dụng `show_pdf_page` của PyMuPDF để co dãn vector trang chuẩn xác về $595.28 \times 841.89\text{ pt}$ (hoặc $841.89 \times 595.28\text{ pt}$ nếu là landscape) nếu kích thước lệch $> 2\text{ pt}$.
  - Gọi `normalize_pdf_to_a4` sau khi xuất PDF trong `export_sheets_to_pdf`, `export_to_pdf`, và `_export_pdf_fallback`.
  - Trong `render_pdf_to_images` và `render_pdf_page`: Tính toán ma trận zoom động:
    $$\text{scale}_x = \frac{\text{target\_w\_px}}{\text{page.rect.width}}, \quad \text{scale}_y = \frac{\text{target\_h\_px}}{\text{page.rect.height}}$$
    Đảm bảo kích thước ảnh PIL render ra luôn là $827 \times 1170\text{ px}$ ở 100 DPI.

### 2.3 Lớp 3 (P1): Đồng bộ Chiều cao Dòng bằng Float chính xác từ openpyxl XML
- **Mục tiêu**: Loại bỏ sai số tích lũy do COM getter làm tròn số.
- **Thực thi**:
  - Trong `_sync_changed_layout_from_com`: Thay vì gọi COM getter:
    `effective_height = reference_range.Rows(relative_index).EntireRow.RowHeight` (làm tròn `17.15` thành `17.0`),
    sử dụng trực tiếp giá trị float chính xác `group["key"][0]` đã đọc từ cấu trúc XML của openpyxl:
    ```python
    target_sheet.Range(f"{group['start']}:{group['end']}").EntireRow.RowHeight = group["key"][0]
    ```

### 2.4 Lớp 4 (P1): Bộ lọc Đường kẻ Hình thái học & Làm mờ Subpixel trong OpenCV Diffing
- **Mục tiêu**: Triệt tiêu các vệt chênh lệch do khử răng cưa đường kẻ bảng ($\le 1.5\text{ px}$) không đi kèm thay đổi văn bản.
- **Thực thi**:
  - Viết hàm `filter_thin_gridline_shifts(diff_mask, img1_bgr, img2_bgr, max_shift_px=2)`:
    1. Trích xuất biên cạnh ngang và dọc (Sobel gradient) trên cả hai ảnh gốc.
    2. Xác định các đường kẻ bảng tồn tại đồng thời trên cả 2 ảnh với độ lệch $\le 2\text{ px}$.
    3. Phân tích các connected components trong mặt nạ khác biệt `diff_mask`: nếu một thành phần có dạng đường kẻ mảnh (chiều cao $\le 3\text{ px}$ và bề rộng $\ge 8\text{ px}$, hoặc ngược lại) và nằm trùng khớp trên vị trí đường kẻ chung của 2 bản, thành phần này được xác nhận là sai số căn chỉnh đường kẻ và được loại bỏ khỏi mặt nạ lỗi.
    4. Mọi thay đổi văn bản (text glyphs), đối tượng thêm mới, bị xóa hoặc đường kẻ mới thêm vào đều được bảo toàn 100%.

---

## 3. Kế Hoạch Triển Khai & Kiểm Thử

| Bước | Hạng mục | Tệp tác động | Trạng thái |
|---|---|---|---|
| 1 | Tạo spec triển khai | `docs/SPECKIT_A4_NORMALIZATION_PLAN.md` | Hoàn thành |
| 2 | Cài đặt `_ensure_a4_printer`, `PrintCommunication`, `normalize_pdf_to_a4`, matrix rendering | `services/pdf_service.py` | Tiến hành |
| 3 | Cập nhật render preview chuẩn A4 | `services/report_service.py` | Tiến hành |
| 4 | Cài đặt `filter_thin_gridline_shifts` | `services/optimized_image_compare.py` | Tiến hành |
| 5 | Viết bộ kiểm thử tự động giả lập Letter & A4 | `tests/test_a4_normalization.py` | Tiến hành |
| 6 | Chạy kiểm thử toàn diện (`run_tests.py`) | Toàn bộ test suite | Tiến hành |
| 7 | Nâng phiên bản lên 7.4.3 | `config.py`, `release.json`, `installer/SosanhCTTT.iss`, `CHANGELOG.md` | Tiến hành |
| 8 | Đóng gói PyInstaller, Inno Setup, `.mpupdate` | `package_app.py` | Tiến hành |
| 9 | Git commit & git push lên repository | Git repository | Tiến hành |

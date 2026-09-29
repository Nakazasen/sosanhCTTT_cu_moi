# 📝 Lịch Sử Thay Đổi (Changelog)

All notable changes to this project will be documented in this file.

---

## [7.4.4] - 2026-09-29 - Tối Ưu Tốc Độ So Sánh (Rollback v7.4.2 Core) & Tinh Chỉnh Biểu Mẫu ĐƯKC

### 🎯 Added & Upgraded
- **Khôi Phục Tốc Độ So Sánh Lõi (Rollback Thuật Toán So Sánh về v7.4.2)**:
  - Loại bỏ các bộ lọc hình thái học đường kẻ đa tầng (`detect_thin_lines`, `filter_thin_gridline_shifts`) và các vòng lặp overthinking gây chậm tiến trình so sánh ở bản v7.4.3.
  - Bảo toàn trọn vẹn giải thuật cân bằng độ sáng Histogram Matching LUT (`match_bgr_crop`, `match_histograms_lut`), kiểm tra tương quan Pearson (`std() < 8.0`, `np.corrcoef >= 0.90`) và dung sai dịch chuyển 1px, giúp so sánh cực nhanh và chính xác.
- **Tinh Chỉnh Tên File Kết Quả Ngắn Gọn & Trực Quan**:
  - Đối với biểu mẫu có tên template dài (`KDTVN-A-PE-BM-014-X Bản yêu cầu đối ứng khẩn cấp New_2026.xlsm`), hệ thống tự động nhận diện và thay thế bằng mã ngắn gọn từ file cũ: `Kết quả_PDF_[VN 36223].xlsx` và `[VN 36223].pdf`.
  - Loại bỏ hoàn toàn nguy cơ vượt quá giới hạn 260 ký tự đường dẫn Windows (MAX_PATH) trên các thư mục mạng sâu.
- **Bảo Vệ Biểu Mẫu ĐƯKC & Cảnh Báo Quyền Ghi**:
  - Tự động khóa nút phương pháp Chụp màn hình (Legacy) khi chọn chế độ ĐƯKC, hiển thị hướng dẫn rõ ràng yêu cầu dùng phương pháp PDF.
  - Hiển thị popup cảnh báo đường dẫn đích khi thư mục mạng không có quyền ghi.

### 🧪 Tests
- Chạy toàn diện 99 unit test đạt tỷ lệ **99/99 PASSED (100% OK)**.

---

## [7.4.3] - 2026-09-15 - Chuẩn Hóa Khổ Trang A4 & Khử Báo Động Giả Đường Kẻ Bảng

### 🎯 Added & Upgraded
- **Khóa Máy In Chuẩn A4 trong Excel COM**:
  - Tự động phát hiện cổng thiết bị máy in `"Microsoft Print to PDF on ..."` từ Windows Registry (`HKCU\Software\Microsoft\Windows NT\CurrentVersion\Devices`) và gán cứng cho `excel.ActivePrinter`.
  - Bọc toàn bộ thiết lập `PageSetup` (`PaperSize = 9` - xlPaperA4, `FitToPagesWide = 1`, `FitToPagesTall = 1`) bằng cặp `excel.PrintCommunication = False` và `finally: excel.PrintCommunication = True`, ngăn chặn triệt để Windows driver bên thứ 3 ép khổ US Letter ($612 \times 792$ pt).
- **Chuẩn Hóa Khổ Trang PDF Chuẩn Sau Khi Xuất (Post-Export Rescaling)**:
  - Tích hợp `PDFService.normalize_pdf_to_a4` bằng PyMuPDF: Tự động kiểm tra và co dãn chính xác mọi trang PDF không đúng kích thước về A4 tiêu chuẩn ($595.28 \times 841.89$ pt).
  - Chuẩn hóa tỷ lệ ma trận rendering ảnh PIL trong `PDFService.render_pdf_to_images` và `ReportService._embed_pdf_preview` về cố định $(827, 1170)$ px ở DPI=100.
- **Đồng Bộ Chiều Cao Dòng Float Chính Xác Từ XML**:
  - `_sync_changed_layout_from_com` chuyển sang gán trực tiếp giá trị float độ chính xác cao lấy từ XML openpyxl thay vì đọc lại thuộc tính `RowHeight` của COM (vốn làm tròn số thành nguyên).
- **Bộ Lọc Khử Lệch Vi Phân Đường Kẻ Bảng (Morphological Subpixel Line Filter)**:
  - Tích hợp giải thuật phát hiện đỉnh cực trị (`detect_thin_lines`) và `filter_thin_gridline_shifts` trong `services/optimized_image_compare.py`.
  - Khử triệt để 110 hộp bôi đỏ vi sai $\le 1.5$ px do khử răng cưa/co dãn bảng trên máy có thiết lập in khác nhau, đồng thời giữ nguyên độ nhạy $100\%$ đối với các thay đổi nội dung chữ số, linh kiện và nét vẽ mới.

### 🧪 Tests
- Bổ sung bộ kiểm thử `tests/test_a4_normalization.py` bao phủ: Chuẩn hóa Letter $\to$ A4, độ phân giải 100 DPI, phân giải ActivePrinter từ Registry, bảo toàn float RowHeight, khử lệch 1px đường kẻ và bắt trọn thay đổi thực tế.

---

## [2026-08-26] - Refactored Deterministic Harness & Accuracy Upgrade

### 🎯 Added
- **Graphify Knowledge Graph**: Tích hợp đồ thị tri thức mã nguồn toàn diện gồm 629 nodes, 979 edges và 41 communities tại `graphify-out/` (`graph.html`, `graph.json`, `GRAPH_REPORT.md`).
- **Comprehensive Documentation Suite**: Viết lại toàn bộ hệ thống tài liệu chuẩn mực:
  - `README.md`: Tổng quan dự án, hướng dẫn cài đặt và sử dụng hiện đại.
  - `ARCHITECTURE.md`: Đặc tả kiến trúc Clean Architecture, vòng đời COM và đa luồng.
  - `CODEBASE.md`: Bản đồ mã nguồn, danh mục hàm, God Nodes và ma trận phụ thuộc.
  - `docs/USER_GUIDE.md`: Cẩm nang hướng dẫn sử dụng chi tiết cho người dùng cuối.
  - `docs/TECHNICAL_SPEC.md`: Đặc tả giải thuật thị giác máy tính và tự động hóa COM.
- **Merged Comparison PDFs**: Tự động gộp file `comparison_ALL_SHEETS.pdf` và `So_sanh_{filename}.pdf` bên cạnh file Excel kết quả.

### 🐛 Fixed
- **Image Comparison Accuracy**: Sửa triệt để lỗi gán cứng `has_diff = True` và thuật toán hash thu nhỏ; thay thế bằng cơ chế đếm điểm ảnh `cv2.countNonZero(mask)` chính xác 100% không phát sinh báo động giả hay bỏ sót sai số nhỏ.
- **PDF Sheet Ordering**: Sửa lỗi đảo ngược thứ tự sheet trong `_export_pdf_fallback` bằng cách dùng `Copy(After=...)` và dọn dẹp các sheet mặc định ban đầu.
- **Preprocessing & Barcode Sync**: Chuẩn hóa hàm `standard_preprocess` phân định rõ file mới (lọc tab xanh `5296274` + thêm `b`) và file cũ (duyệt tất cả sheet + đồng bộ `b` theo file mới).
- **Windows Console Unicode**: Cấu hình `sys.stdout` và `sys.stderr` sang `utf-8` với `errors='replace'` trong `utils.py`, loại bỏ hoàn toàn lỗi crash `UnicodeEncodeError: 'cp932'` khi ghi log tiếng Việt.
- **Unit Test Suite**: Nâng cấp toàn bộ 29 Unit Test trong `run_tests.py` đạt tỷ lệ **29/29 PASSED (100% OK)**.

---

## [2026-03-03] - Performance Optimization & OpenCV Integration

### Added
- **Performance Audit Report**: Báo cáo chi tiết tại `docs/reports/audit_performance_20260303.md`.
- **Integration Tests**: Thêm các bài test trong `tests/test_performance_fixes.py` bao phủ toàn bộ các logic tối ưu hiệu suất.
- **OpenCV Screenshot Comparison**: Bật chế độ so sánh ảnh bằng OpenCV cho Screenshot Workflow, tăng tốc độ 10–50x.

### Fixed
- **Excel COM Lifecycle**: Giữ instance Excel sống trong suốt quá trình retry, tiết kiệm 10–30s khởi động Excel.
- **Memory Cleanup**: Giải phóng bộ nhớ ảnh (`del new_images`) ngay sau khi hoàn thành từng file.

---

## [2026-01-31] - Core Stability & Sanitization

### Added
- **Hidden Logging**: Ghi log debug an toàn vào `app_debug.log`.
- **Strict Filename Sanitization**: Hàm `sanitize_filename_strict` trong `utils.py`.
- **Unit Tests**: Bổ sung `tests/test_pdf_fix_and_logging.py`.

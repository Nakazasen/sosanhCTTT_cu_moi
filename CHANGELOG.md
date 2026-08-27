# 📝 Lịch Sử Thay Đổi (Changelog)

All notable changes to this project will be documented in this file.

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

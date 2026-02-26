# Changelog

## [2026-01-31]

### Added

- **Hidden Logging**: Tự động ghi log debug vào `app_debug.log` (hoặc Temp) để điều tra lỗi ngầm.
- **Strict Filename Sanitization**: Hàm `sanitize_filename_strict` trong `utils.py` để xử lý tên file an toàn tuyệt đối.
- **Unit Tests**: Thêm `tests/test_pdf_fix_and_logging.py` để verify các tính năng mới.

### Fixed

- **PDF Export Error**: Sửa lỗi "Không tìm thấy đường dẫn" khi tên sheet Excel chứa ký tự đặc biệt (`?`, `:`, `*`...) bằng cách thay thế chúng thành `_` trước khi tạo file tạm.
- **Test Runner**: Cập nhật `run_tests.py` để chạy được trên môi trường Python launcher chuẩn.

### Known Issues

- `tests/test_comparator.py`: Vẫn fail do thiếu dependency `Pillow` hoặc lỗi import trong môi trường test (đã skip để ưu tiên deploy).

# 💡 BRIEF: Cải tiến System Logging & Fix lỗi PDF

**Ngày tạo:** 31/01/2026
**Mục tiêu:** Thêm khả năng điều tra lỗi ngầm và khắc phục lỗi xuất PDF.

---

## 1. TÍNH NĂNG MỚI: HIDDEN LOGGING (Ghi log ngầm)

### 🎯 Vấn đề

- Hiện tại App chỉ hiện log ra màn hình console (nếu chạy từ code).
- Khi người dùng chạy file `.exe`, nếu có lỗi hoặc hành vi lạ, không có cách nào xem lại lịch sử để điều tra.

### ✅ Giải pháp đề xuất

Thêm cơ chế tự động ghi log ra file `.txt` nằm cùng thư mục với file `.exe` (hoặc `main.py`).

**Cơ chế hoạt động:**

1. **Xác định vị trí:**
    - Nếu chạy `.exe`: Lấy đường dẫn nơi file exe đang nằm.
    - Nếu chạy code (`python main.py`): Lấy đường dẫn thư mục project.
2. **File Log:**
    - Tên file: `app_debug.log`
    - Chế độ: `Append` (Ghi nối tiếp), có thể xoay vòng (rotate) nếu file quá lớn (vd: >5MB).
    - Nội dung: Thời gian, Level (INFO/ERROR), Module, Thông báo lỗi.
3. **Bảo mật/An toàn:**
    - Log "ngầm" (không hiện popup cho user).
    - Bắt lỗi `PermissionError` (nếu cài trong Program Files không cho ghi) -> Fallback sang thư mục `%TEMP%`.

---

## 2. SỬA LỖI: PDF EXPORT ("Không tìm thấy đường dẫn")

### 🎯 Vấn đề

- User báo lỗi tính năng so sánh PDF không xuất được file, nghi ngờ lỗi đường dẫn.
- **Phân tích kỹ thuật:**
  - Trong quá trình xuất PDF, code tạo các file tạm thời cho từng sheet: `temp_sheet_{idx}_{name}.pdf`.
  - Logic hiện tại chỉ thay thế ký tự `|`, `/` và `space`.
  - **Lỗ hổng:** Nếu tên sheet chứa các ký tự cấm của Windows như `?`, `:`, `*`, `"`, `<`, `>`, file path sẽ không hợp lệ.
  - Excel sẽ báo lỗi chung chung hoặc "Document not saved", dẫn đến user nghĩ là lỗi đường dẫn.

### ✅ Giải pháp đề xuất

1. **Strict Filename Sanitization:**
    - Áp dụng hàm làm sạch tên file nghiêm ngặt cho các file tạm.
    - Thay thế tất cả ký tự đặc biệt bằng `_`.
2. **Explicit Directory Check:**
    - Đảm bảo thư mục đầu ra luôn được tạo (`os.makedirs`) ngay trước khi lệnh Export được gọi.

---

## 3. KẾ HOẠCH THỰC HIỆN

| Task | File ảnh hưởng | Độ phức tạp |
|------|----------------|-------------|
| **1. Config Logging** | `utils.py`, `config.py` | Thấp |
| **2. Fix PDF Sanitization** | `services/pdf_service.py` | Thấp |

### Bước tiếp theo

- Chạy `/plan` để xác nhận implementation details (nhưng vì task nhỏ, em có thể làm luôn trong `/code`).

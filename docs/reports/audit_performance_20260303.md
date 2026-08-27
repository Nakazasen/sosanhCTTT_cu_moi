# 🏥 Audit Report - Performance Focus
**Date:** 2026-03-03  
**Scope:** D) Performance Focus - Tốc độ xử lý, tối ưu Excel/PDF  
**Bác sĩ Code:** Khang (Antigravity Auditor v2.1)

---

## Summary

| Mức độ | Số lượng |
|--------|---------|
| 🔴 Critical (Phải sửa ngay) | 2 |
| 🟡 Warning (Nên sửa) | 4 |
| 🟢 Suggestion (Tùy chọn) | 3 |
| ✅ Tốt (Đã làm đúng) | 6 |

---

## ✅ Điểm Mạnh (Đã Làm Đúng)

Trước khi vào vấn đề, cần công nhận những phần đã được tối ưu tốt:

1. **OpenCV Short-circuit** (`optimized_image_compare.py`): Đã dùng `quick_compare_hash()` để bỏ qua so sánh nặng nếu 2 ảnh giống nhau 100%. Xuất sắc!
2. **ThreadPoolExecutor** (`comparator.py:470`): Đã xử lý song song các page PDF với tối đa 4 threads.
3. **ScreenUpdating / EnableEvents = False** (`excel_service.py:42-47`): Đã tắt rendering Excel khi chạy ngầm → tăng tốc đáng kể.
4. **RotatingFileHandler** (`utils.py:48`): Log file tự xoay vòng sau 5MB, không làm nặng ổ đĩa.
5. **Calculation = xlCalculationManual** (`pdf_service.py:120`): Đã tắt tính toán tự động khi export PDF.
6. **Graceful fallback chain**: Excel → PDF → PIL → OpenCV → PyMuPDF đều có fallback rõ ràng.

---

## 🔴 Critical Issues (Phải Sửa Ngay)

### 1. Excel Instance Tạo Lại Liên Tục Khi Export PDF

**File:** `pdf_service.py` - `export_sheets_to_pdf()` (L332) & `export_sheets_to_pdf_with_retry()` (L338)

**Triệu chứng:** Mỗi lần gọi `export_sheets_to_pdf()`, hàm sẽ chạy `_cleanup_excel()` ở cuối `finally`. Nhưng hàm `export_sheets_to_pdf_with_retry()` lại gọi `export_sheets_to_pdf()` nhiều lần (tối đa 3 lần). Điều này có nghĩa là:

```
Lần 1: Khởi động Excel → xử lý → Tắt Excel
Lần 2: Khởi động Excel lại → xử lý → Tắt Excel  ← LÃng phí!
Lần 3: Khởi động Excel lại → xử lý → Tắt Excel  ← LÃng phí!
```

**Hậu quả:** Mỗi lần khởi động Excel COM tốn **2-5 giây**. Với 3 file, mỗi file retry 3 lần = mất hơn **30 giây** chỉ để khởi động Excel.

**Gợi ý sửa:** Truyền Excel instance đã có vào `export_sheets_to_pdf()` thay vì để hàm tự quản lý lifecycle, hoặc chỉ cleanup ở hàm wrapper `_with_retry`.

---

### 2. Screenshot Workflow Không Dùng OpenCV

**File:** `comparator.py` - `_process_screenshot_workflow()` (L628-694)

**Triệu chứng:** Trong khi `_process_legacy_pdf_workflow()` đã được tối ưu để dùng OpenCV (10-50x nhanh hơn), thì `_process_screenshot_workflow()` vẫn dùng PIL thuần túy:

```python
# Trong Screenshot Workflow - CHẬM:
diff = ImageChops.difference(img_new.convert('RGB'), img_old.convert('RGB'))
mask = diff_gray.point(lambda x: 255 if x > threshold else 0)  # Chậm với ảnh lớn

# Trong PDF Workflow - NHANH (có sẵn):
left_img, right_img = compare_images_opencv(...)  # 10-50x nhanh hơn
```

**Hậu quả:** Nếu người dùng dùng chế độ Screenshot, tốc độ so sánh ảnh chậm hơn 10-50 lần so với chế độ PDF. Không nhất quán.

**Gợi ý sửa:** Import và dùng `compare_images_opencv` từ `optimized_image_compare` trong `_process_screenshot_workflow()` giống như đã làm trong PDF workflow.

---

## 🟡 Warnings (Nên Sửa)

### 3. DPI Mặc Định 100 - Có Thể Tối Ưu Thêm

**File:** `config.py` - `DEFAULT_DPI = 100`

**Triệu chứng:** DPI 100 render mỗi trang PDF thành ảnh khoảng **827x1169 pixels**. Đây là kích thước hợp lý, nhưng khi xử lý nhiều trang song song trong ThreadPoolExecutor, bộ nhớ RAM có thể bị thiếu.

**Hậu quả:** Với 10 file × 5 sheet × 2 ảnh (cũ + mới) = 100 ảnh trong RAM cùng lúc → ~300-500MB RAM.

**Gợi ý sửa:** Thêm option "Chế độ nhẹ" với DPI=72 cho máy yếu. Hoặc render ảnh từng cặp và giải phóng ngay sau khi so sánh xong.

---

### 4. `quick_compare_hash` Quá Đơn Giản

**File:** `optimized_image_compare.py:181-203`

**Triệu chứng:** Hàm so sánh nhanh hiện dùng resize ảnh xuống 32×32 pixel và so sánh mean. Điều này có thể bỏ lỡ những thay đổi nhỏ (ví dụ: một chữ số thay đổi trong bảng số liệu).

```python
# Hiện tại - không đủ nhạy:
return mean_diff < 5.0  # Ngưỡng quá cao
```

**Hậu quả:** Có thể bỏ lỡ sai khác nhỏ quan trọng trong CTTT (thanh toán), báo cáo "OK" khi thực ra có thay đổi.

**Gợi ý sửa:** Hạ ngưỡng xuống `< 2.0`, hoặc dùng perceptual hash (phash) thay vì mean.

---

### 5. `_export_pdf_fallback` Tạo Excel Instance Riêng Biệt

**File:** `pdf_service.py:395-533`

**Triệu chứng:** Hàm fallback tạo một Excel COM instance hoàn toàn mới, độc lập với `self.excel_app`, rồi cleanup sau. Điều này tốt về isolation nhưng tốn thêm 2-5 giây khởi động Excel.

**Hậu quả:** Mỗi lần fallback = thêm 2-5 giây. Với nhiều file lỗi, thời gian cộng dồn đáng kể.

**Gợi ý sửa:** Reuse `self.excel_app` trong fallback thay vì tạo instance mới, hoặc dùng `DispatchEx` để tạo nhanh hơn.

---

### 6. `_capture_sheets_to_images` Không Dùng DPI Config

**File:** `comparator.py:786`

```python
zoom_level = self.settings.get('zoom', 46) if self.settings else 46
```

**Triệu chứng:** Zoom level mặc định cố định là 46. Đây là giá trị cho màn hình, không phải DPI cho render ảnh. Không liên kết với `DEFAULT_DPI` trong `config.py`.

**Hậu quả:** Không đồng nhất giữa 2 workflow. Kết quả ảnh có thể lệch tỉ lệ giữa PDF và Screenshot mode.

---

## 🟢 Suggestions (Tùy Chọn - Nếu Muốn Tối Ưu Hơn)

### 7. Cache Danh Sách Sheet Màu Xanh

**File:** `comparator.py` - `_process_legacy_pdf_workflow()` (L352) và `_process_screenshot_workflow()` (L588)

Hai workflow đều gọi `get_colored_sheets()` / lặp qua sheet để tìm màu xanh trên **cùng một file**. Có thể cache kết quả ở `ExcelService` để không đọc lại file nếu đã xử lý.

### 8. Xử Lý Song Song Cả File (Không Chỉ Page)

Hiện tại, các file được xử lý tuần tự (sequential). Có thể dùng `ProcessPoolExecutor` để xử lý song song nhiều file cùng lúc, đặc biệt hữu ích khi có nhiều file input.

> ⚠️ **Lưu ý:** Excel COM không thread-safe, nên cần dùng `ProcessPoolExecutor` (process riêng) thay vì `ThreadPoolExecutor`.

### 9. Giải Phóng Memory Sau Mỗi File

**File:** `comparator.py:385-386`

```python
new_images = self.pdf_service.render_pdf_to_images(pdf_new_path, dpi)
old_images = self.pdf_service.render_pdf_to_images(pdf_old_path, dpi)
```

Sau khi so sánh xong tất cả page của một file, nên `del new_images` và `del old_images` để Python giải phóng RAM trước khi xử lý file tiếp theo.

---

## 📊 Phân Tích Thời Gian Ước Tính (Với 5 File, Mỗi File 3 Sheet)

| Bước | Thời gian hiện tại | Sau tối ưu |
|------|-------------------|-----------|
| Excel init (mỗi retry) | 2-5s × 3 lần | 2-5s × 1 lần |
| PDF Export (per file) | ~10-15s | ~10-15s (không đổi) |
| Image comparison (PIL) | ~2-5s/sheet | ~0.1-0.5s/sheet (OpenCV) |
| **Tổng (5 file × 3 sheet)** | **~5-8 phút** | **~2-4 phút** |

---

## ⏭️ Next Steps

```
📋 Bạn muốn làm gì tiếp theo?

1️⃣ Xem báo cáo chi tiết trước (đang xem)
2️⃣ Sửa Critical Issue #1: Tối ưu Excel lifecycle trong retry
3️⃣ Sửa Critical Issue #2: Bật OpenCV cho Screenshot workflow
4️⃣ Sửa tất cả Warning issues (3-6)
5️⃣ 🔧 FIX ALL - Tự động sửa tất cả lỗi có thể sửa

Gõ số (1-5) để chọn:
```

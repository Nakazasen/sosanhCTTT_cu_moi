# 🔧 ĐẶC TẢ KỸ THUẬT & GIẢI THUẬT (TECHNICAL SPECIFICATION)

> **Tài liệu đặc tả giải thuật nội bộ, kỹ thuật xử lý ảnh máy tính và tự động hóa COM cho Phần mềm So sánh CTTT.**

---

## 1. Ngăn Xếp Công Nghệ (Technology Stack)

| Thành phần | Thư viện / Công nghệ | Vai trò kỹ thuật |
|---|---|---|
| **Ngôn ngữ** | Python 3.9+ (Typed) | Ngôn ngữ phát triển cốt lõi |
| **Giao diện (GUI)** | Tkinter / `tkinter.ttk` | Giao diện đồ họa native Windows, giao tiếp đa luồng an toàn |
| **Tự động hóa Office** | `pywin32` (`win32com.client`) | Giao tiếp COM cục bộ điều khiển Microsoft Excel engine |
| **Xử lý đồ họa & PDF** | PyMuPDF (`fitz`), Pillow (`PIL`), `reportlab` | Render vector PDF sang bitmap và tạo tài liệu PDF |
| **Thị giác máy tính (CV)** | OpenCV (`cv2`), NumPy | Xử lý ma trận ảnh, tính toán chênh lệch màu, dãn nở hình học (Dilation), tìm đường viền (Contours) |
| **Kiểm thử tự động** | `unittest`, `unittest.mock` | Bộ kiểm thử 29 ca kiểm thử tự động không phụ thuộc môi trường |

---

## 2. Giải Thuật So Sánh Ảnh (Computer Vision Diffing Pipeline)

Thuật toán trong [`services/optimized_image_compare.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/optimized_image_compare.py) được thiết kế theo quy trình 6 bước:

```text
[Ảnh Mới & Cũ]
      │
      ▼
 1. Resize LANCZOS4 (nếu khác kích thước)
      │
      ▼
 2. Absolute Difference: Diff = |Img_New - Img_Old|
      │
      ▼
 3. Grayscale Conversion & Binary Thresholding: Mask = (Diff_Gray > Threshold)
      │
      ▼
 4. Pixel Difference Counter: N = countNonZero(Mask)
      │
   ┌──┴──────────────────────────┐
   │ N == 0                      │ N > 0 (Có sai khác)
   ▼                             ▼
 [Bỏ qua (OK)]             5. Morphological Dilation (Kernel 3x3)
                                 │
                                 ▼
                           6. Alpha Blending + Contour Drawing
                                 │
                                 ▼
                           [Ảnh Side-by-Side Highlight]
```

### Bước 1: Đồng bộ hóa kích thước ma trận
Nếu hai ảnh có độ phân giải hoặc tỷ lệ khác nhau, ảnh cũ được nội suy sang kích thước ảnh mới bằng thuật toán `cv2.INTER_LANCZOS4` để đảm bảo độ sắc nét cao nhất.

### Bước 2: Tính toán sai biệt tuyệt đối (Absolute Difference)
$$\text{Diff}(x, y) = |\text{Img}_{\text{new}}(x, y) - \text{Img}_{\text{old}}(x, y)|$$

### Bước 3: Nhị phân hóa mặt nạ (Binary Masking)
$$\text{Mask}(x, y) = \begin{cases} 255 & \text{nếu } \text{Grayscale}(\text{Diff}(x, y)) \ge \text{Threshold} \\ 0 & \text{ngược lại} \end{cases}$$

### Bước 4: Đếm điểm ảnh khác biệt & Xác định trạng thái
$$N = \sum_{x, y} \frac{\text{Mask}(x, y)}{255}$$
- Nếu $N = 0$: Hai trang hoàn toàn trùng khớp $\rightarrow$ Trả về `has_diff = False`.
- Nếu $N > 0$: Có sự thay đổi nội dung $\rightarrow$ Trả về `has_diff = True`.

### Bước 5: Dãn nở hình học (Morphological Dilation)
Áp dụng phép toán dãn nở ma trận với phần tử cấu trúc vuông kích thước $K \times K$ (mặc định $3 \times 3$) lặp $M$ lần (mặc định 2 lần) để gom các điểm ảnh chữ rời rạc thành một khối highlight liền mạch:
$$\text{Mask}_{\text{dilated}} = \text{Mask} \oplus B$$

### Bước 6: Phủ màu trong suốt (Alpha Blending) & Vẽ viền (Contours)
$$\text{Overlay}(x, y) = (1 - \alpha) \cdot \text{Img}_{\text{new}}(x, y) + \alpha \cdot \text{Color}_{\text{highlight}}$$
Đồng thời, hàm `cv2.findContours` tìm kiếm các đường bao ngoài và vẽ viền sắc nét bằng `cv2.drawContours`.

---

## 3. Tự Động Hóa COM Excel & Xuất PDF

Trong [`services/pdf_service.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/pdf_service.py), để đảm bảo định dạng xuất PDF chuẩn từng trang và không bị ngắt trang lộn xộn:

```python
# Cấu hình PageSetup chuẩn cho từng Worksheet
ps = sheet.PageSetup
ps.Orientation = 1        # xlPortrait (Dọc)
ps.PaperSize = 9          # xlPaperA4 (Khổ A4)
ps.Zoom = False           # Tắt zoom tự do để kích hoạt FitToPages
ps.FitToPagesWide = 1     # Ép vừa đúng 1 trang chiều ngang
ps.FitToPagesTall = 1     # Ép vừa đúng 1 trang chiều dọc
ps.LeftMargin = 0         # Triệt tiêu lề để hiển thị tối đa dữ liệu
ps.RightMargin = 0
ps.TopMargin = 0
ps.BottomMargin = 0
ps.CenterHorizontally = True
ps.CenterVertically = True
```

### Bảo toàn thứ tự sao chép Sheet:
Khi dùng phương pháp fallback tạo Workbook mới, các sheet được sao chép bằng lệnh `Copy(After=new_workbook.Sheets(new_workbook.Sheets.Count))` để đảm bảo giữ nguyên vẹn 100% thứ tự từ trái qua phải của các sheet trong bảng tính gốc.

---

## 4. Mô Hình Đa Luồng & Bộ Nhớ (Concurrency & Memory Safety)

1. **Giao diện không bị đóng băng**: UI Tkinter chạy trên Main Thread, toàn bộ tác vụ tính toán so sánh chạy trên một `threading.Thread(daemon=True)`.
2. **Song song hóa tác vụ so sánh (ThreadPoolExecutor)**: 
   - Quá trình xử lý ảnh đối chiếu giữa các trang PDF chạy song song với `max_workers = min(4, num_pages)` luồng.
   - Giúp tận dụng tối đa CPU đa nhân mà không làm nghẽn bộ nhớ.
3. **Giải phóng tài nguyên bộ nhớ**:
   - Các biến giữ mảng ảnh `new_images` và `old_images` được thu hồi bằng lệnh `del` ngay sau khi so sánh xong một cặp file.
   - Các tệp ảnh trung gian dạng bitmap được xóa khỏi đĩa cứng sau khi chèn vào bảng tính kết quả.

# 📖 CẨM NANG HƯỚNG DẪN SỬ DỤNG - PHẦN MỀM SO SÁNH CTTT

> **Tài liệu hướng dẫn sử dụng chi tiết dành cho người dùng cuối (Kế toán, Kiểm toán, Chuyên viên xử lý Chứng Từ Thanh Toán).**

---

## 📑 MỤC LỤC
1. [Giới thiệu tổng quan](#1-giới-thiệu-tổng-quan)
2. [Yêu cầu chuẩn bị dữ liệu](#2-yêu-cầu-chuẩn-bị-dữ-liệu)
3. [Hướng dẫn thao tác cơ bản (4 bước)](#3-hướng-dẫn-thao-tác-cơ-bản-4-bước)
4. [Các tính năng nâng cao & Cài đặt](#4-các-tính-năng-nâng-cao--cài-đặt)
   - [Tự động thêm 'b' (Barcode matching)](#41-tự-động-thêm-b-barcode-matching)
   - [Tùy chỉnh màu sắc & độ trong suốt Highlight](#42-tùy-chỉnh-màu-sắc--độ-trong-suốt-highlight)
   - [Độ phân giải DPI & Ngưỡng phát hiện sai khác](#43-độ-phân-giải-dpi--ngưỡng-phát-hiện-sai-khác)
   - [Chế độ màn hình (PC / VPS)](#44-chế-độ-màn-hình-pc--vps)
5. [Đọc và hiểu Báo cáo kết quả](#5-đọc-và-hiểu-báo-cáo-kết-quả)
6. [Các lỗi thường gặp & Cách xử lý nhanh (FAQ)](#6-các-lỗi-thường-gặp--cách-xử-lý-nhanh-faq)

---

## 1. Giới thiệu tổng quan

Phần mềm **So sánh Chứng Từ Thanh Toán (CTTT)** là công cụ tự động hóa giúp bạn đối chiếu từng trang bảng tính giữa file CTTT mới và file CTTT cũ:
- Tự động tìm kiếm các sheet có màu tab xanh lá cây (`#50C878` / màu `5296274`).
- Đối chiếu số liệu, nội dung, bảng biểu và ký tự.
- Tô màu viền và nền đỏ nổi bật (**Highlight**) tại đúng vị trí có sự thay đổi.
- Xuất ra file Excel kết quả chứa hình ảnh so sánh song song (**Ảnh cũ bên trái | Ảnh mới có highlight bên phải**).

---

## 2. Yêu cầu chuẩn bị dữ liệu

Để phần mềm hoạt động tối ưu và chính xác nhất:
1. **File CTTT Mới**: Các sheet cần so sánh phải được đặt **màu Tab là màu Xanh lá cây** (Green Tab Color). Các sheet màu khác hoặc không có màu tab sẽ được tự động bỏ qua.
2. **File CTTT Cũ**: Phần mềm sẽ tự động tìm kiếm sheet tương ứng theo tên (hoặc các biến thể tên có dấu gạch ngang `-`, gạch dưới `_`, hoặc có/không có tiền tố `b`).
3. **Thư mục lưu trữ**: Gom các file CTTT Mới vào một thư mục riêng và các file CTTT Cũ tương ứng vào một thư mục riêng.

---

## 3. Hướng dẫn thao tác cơ bản (4 bước)

```text
[Chọn Thư mục Mới] ──> [Chọn Thư mục Cũ] ──> [Kiểm tra Cài đặt] ──> [BẮT ĐẦU SO SÁNH] ──> [Xác nhận cặp file]
```

### 🔹 Bước 1: Chọn thư mục file mới
- Nhấn nút **"Chọn thư mục"** tại mục **"1. THƯ MỤC CTTT MỚI"** (hoặc gõ trực tiếp đường dẫn).
- Phần mềm sẽ tự động quét và hiển thị số lượng file Excel tìm thấy.

### 🔹 Bước 2: Chọn thư mục file cũ
- Nhấn nút **"Chọn thư mục"** tại mục **"2. THƯ MỤC CTTT CŨ"**.
- Số lượng file cũ cần tương ứng với số lượng file mới.

### 🔹 Bước 3: Kiểm tra cài đặt
- Mặc định, tùy chọn **"Sử dụng phương pháp PDF"** đã được bật (đây là phương pháp có độ sắc nét và tốc độ cao nhất).
- Nếu các sheet trong file mới có mã vạch bắt đầu bằng chữ `b` (ví dụ: `b01-CTTT`) mà file cũ là `01-CTTT`, hãy tích chọn ô **"Tự động thêm 'b' nếu file cũ không có"**.

### 🔹 Bước 4: Nhấn "BẮT ĐẦU SO SÁNH" & Xác nhận cặp file
1. Nhấn nút lớn màu xanh **"BẮT ĐẦU SO SÁNH"**.
2. Một hộp thoại **"Xác nhận các cặp file so sánh"** sẽ xuất hiện:
   - Bạn có thể kiểm tra xem từng file mới đã khớp đúng với file cũ tương ứng hay chưa.
   - Nếu thứ tự chưa khớp, bạn có thể chọn một file và nhấn nút **"▲ Lên"** hoặc **"▼ Xuống"** để đổi vị trí, hoặc nhấn **"Kéo & Thả"** để sắp xếp.
3. Nhấn nút **"Bắt đầu"** trên hộp thoại để tiến trình so sánh tự động chạy.
4. Khi hoàn tất, thư mục chứa kết quả sẽ tự động được mở ra trong File Explorer.

---

## 4. Các tính năng nâng cao & Cài đặt

### 4.1. Tự động thêm 'b' (Barcode matching)
- Khi lập chứng từ mới, một số hệ thống tự động thêm tiền tố `b` vào tên sheet để đánh dấu barcode.
- Khi bật tính năng này, phần mềm sẽ tự động tìm kiếm sheet tương ứng trong file cũ (dù có hay không có chữ `b`) và chuẩn hóa đồng bộ để không bị mất sheet khi so sánh.

### 4.2. Tùy chỉnh màu sắc & độ trong suốt Highlight
- **Màu Viền (Outline Color)**: Mặc định là màu Đỏ (`#ff0000`). Bạn có thể click vào ô màu để đổi sang màu khác (ví dụ: Vàng, Cam, Xanh dương).
- **Màu Nền Tô (Fill Color)**: Vùng màu phủ mờ lên phần nội dung bị thay đổi.
- **Độ trong suốt (Opacity %)**: Mặc định là `40%`. Tăng lên để màu đậm hơn, hoặc giảm xuống để nhìn rõ chữ bên dưới lớp highlight.

### 4.3. Độ phân giải DPI & Ngưỡng phát hiện sai khác
- **DPI Render PDF**: Mặc định là `100 DPI` (cân bằng hoàn hảo giữa tốc độ và độ nét). Bạn có thể nâng lên `150` hoặc `200` nếu cần xem chi tiết các đường kẻ siêu mảnh.
- **Ngưỡng sai khác (Diff Threshold)**: Mặc định `40`. Giá trị từ `0` (nhạy tuyệt đối với mọi độ lệch màu nhỏ) đến `255`.

### 4.4. Chế độ màn hình (PC / VPS)
- **Màn hình PC**: Tự động đặt mức Zoom `46%` phù hợp với độ phân giải màn hình máy tính văn phòng tiêu chuẩn.
- **Màn hình VPS / Remote Desktop**: Tự động đặt mức Zoom `100%` để hiển thị đầy đủ trên môi trường máy chủ ảo.
- **Màn hình phụ (Secondary)**: Mức Zoom `60%`.

---

## 5. Đọc và hiểu Báo cáo kết quả

Sau khi hoàn tất, thư mục kết quả `Ket_qua_so_sanh_YYYYMMDD_HHMMSS` sẽ chứa các tệp sau:

| Tên tệp | Mô tả chi tiết |
|---|---|
| `Kết quả_PDF_{TênFile}.xlsx` | File Excel kết quả chính. Mỗi sheet tương ứng với một trang CTTT có sai khác, chứa ảnh phóng to đối chiếu. |
| `comparison_ALL_SHEETS.pdf` | File PDF tổng hợp tất cả các trang có sai khác của toàn bộ các file được so sánh. |
| `So_sanh_{TênFile}.pdf` | File PDF so sánh riêng cho từng file (nếu có từ 2 sheet sai khác trở lên). |
| `{TênFile}.pdf` | Bản xuất PDF gốc của file CTTT mới để bạn lưu trữ hoặc in ấn. |

### Cách đọc ảnh so sánh trong Excel:
- **Nửa bên trái (Ảnh Cũ)**: Thể hiện nguyên trạng chứng từ cũ.
- **Nửa bên phải (Ảnh Mới)**: Thể hiện chứng từ mới, trong đó các ô số liệu hoặc câu chữ bị sửa đổi sẽ được **khoanh viền đỏ và phủ nền đỏ nhạt**.
- Nếu 2 sheet **hoàn toàn giống nhau**, phần mềm sẽ ghi nhận `OK: Không có sai khác` và không chèn ảnh thừa vào Excel để giữ file nhẹ và sạch.

---

## 6. Các lỗi thường gặp & Cách xử lý nhanh (FAQ)

### ❓ Câu hỏi 1: Tại sao phần mềm báo "Không tìm thấy sheet màu xanh"?
- **Nguyên nhân**: File Excel mới của bạn chưa được tô màu xanh cho tab của sheet cần so sánh.
- **Cách khắc phục**: Mở file Excel mới, click chuột phải vào tab của sheet -> chọn **Tab Color** -> chọn màu Xanh lá cây (Green) -> Lưu file và chạy lại.

### ❓ Câu hỏi 2: Excel bị treo hoặc hiện thông báo "File is locked by another process"?
- **Nguyên nhân**: File Excel đang được mở bởi người dùng hoặc có một tiến trình `EXCEL.EXE` ngầm bị treo.
- **Cách khắc phục**:
  1. Đóng tất cả các cửa sổ Excel đang mở trên máy tính.
  2. Mở Task Manager (Ctrl + Shift + Esc) và đóng các tiến trình `Microsoft Excel` nếu có.
  3. Chạy lại phần mềm So sánh CTTT.

### ❓ Câu hỏi 3: Làm sao để chuyển giao diện sang Tiếng Anh?
- Nhấn vào menu **Cài đặt** (hoặc biểu tượng quả cầu) trên thanh menu -> chọn **English**. Toàn bộ giao diện sẽ chuyển ngữ tức thì.

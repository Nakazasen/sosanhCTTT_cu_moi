# 📊 Phần Mềm So Sánh Chỉ Thị Thao Tác (CTTT) - Refactored Edition

> **Ứng dụng đối chiếu & so sánh trực quan các bảng tính Chỉ Thị Thao Tác (Excel CTTT Mới vs Cũ) tự động, hiệu năng cao với giao diện hiện đại, thuật toán phát hiện sai khác độ chính xác cao và hỗ trợ đa ngôn ngữ 4 thứ tiếng.**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Modern%20Tkinter-blue)](https://docs.python.org/3/library/tkinter.html)
[![OpenCV](https://img.shields.io/badge/Computer%20Vision-OpenCV-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![PyMuPDF](https://img.shields.io/badge/PDF%20Engine-PyMuPDF%20(fitz)-FF0000)](https://pymupdf.readthedocs.io/)
[![Tests](https://img.shields.io/badge/Tests-66%2F66%20Passing-brightgreen)](file:///d:/Sandbox/Sosanh_CTTT_cu_moi/Refactored/run_tests.py)
[![Languages](https://img.shields.io/badge/Languages-VI%20%7C%20EN%20%7C%20ZH%20%7C%20JA-orange)](#-hỗ-trợ-4-ngôn-ngữ-hoàn-chỉnh)

---

## 🌟 Điểm nổi bật & Tính năng chính

- ⚡ **Tốc độ vượt trội với OpenCV & Multithreading**: Tự động so sánh ma trận điểm ảnh với OpenCV và xử lý song song đa luồng (`ThreadPoolExecutor`), tăng tốc độ 10–50x so với phương pháp chụp màn hình cũ.
- 🎯 **Phát hiện sai lệch chính xác 100%**: Thuật toán `absdiff` và dynamic mask thresholding phát hiện chuẩn xác từng thay đổi nhỏ (chữ số, ký tự, ngày tháng, mã barcode) mà không gây báo động giả (*false positive*) hay bỏ sót (*false negative*).
- 📑 **3 Chế độ so sánh tài liệu chuyên sâu**:
  1. **1. CTTT thông thường (Sheet tab XANH LÁ)**: Tự động nhận diện và so sánh các sheet có tab màu xanh lá tiêu chuẩn.
  2. **2. CTTT thuộc Tờ Phát Hành ĐƯKC (Sheet hiển thị)**: So sánh tất cả các sheet đang hiển thị (visible) trong file.
  3. **3. Tờ Phát Hành ĐƯKC & Khác (Sheet 'Form')**: Chuyên dụng để so sánh cấu trúc biểu mẫu tờ phát hành tại sheet `'Form'`.
- 🌐 **Hỗ trợ 4 ngôn ngữ hoàn chỉnh**:
  - Hỗ trợ đầy đủ **Tiếng Việt 🇻🇳**, **English 🇬🇧**, **中文 (简体) 🇨🇳**, **日本語 🇯🇵**.
  - Chuyển đổi ngôn ngữ tức thì (**Hot-swap UI**) không cần khởi động lại ứng dụng.
- 🚦 **Quy trình 5 bước kiểm soát chặt chẽ (5-Step Gated Workflow)**:
  - Hệ thống step badge màu sắc trực quan (Đã xong ●, Đang thực hiện ●, Đang khóa ○, Bị lỗi ●).
  - Tự động mở khóa từng bước theo trình tự, ngăn ngừa lỗi thao tác sớm.
- ⚠️ **Thông báo lỗi thân thiện & có hướng dẫn khắc phục**:
  - Mọi lỗi xác thực file và chế độ tài liệu đều chỉ rõ: **Vị trí lỗi (Where)**, **Nguyên nhân (Why)**, và **Hướng dẫn khắc phục cụ thể (How to fix)** kèm ký hiệu `👉 Hướng dẫn`.
- 🎨 **Giao diện Modern UI trực quan**:
  - Hộp thoại kéo thả sắp xếp cặp file (Drag & Drop confirmation dialog) hỗ trợ thêm/xóa file từng bên hoặc cả hai bên.
  - Bảng chọn màu highlight tùy biến (Base, Outline, Fill Color) và thanh trượt độ trong suốt (Opacity).
  - Chế độ hiển thị màn hình thông minh (PC, VPS, Màn hình phụ).
- 🔄 **Tự động cập nhật phần mềm nền (Auto-Update Service)**:
  - Tự động kiểm tra bản cập nhật mới từ thư mục chia sẻ nội bộ (LAN / SMB Share).
  - Tải về và xác thực hash bảo mật trước khi kích hoạt bộ cài Inno Setup tự động.
- 📑 **Báo cáo kết quả toàn diện**:
  - Tạo file Excel kết quả độc lập chèn trực tiếp ảnh so sánh side-by-side (Cũ bên trái | Mới bên phải có highlight).
  - Tự động gộp file PDF so sánh tổng hợp nhiều trang.
- 🛡️ **Quản lý tài nguyên COM & Bộ nhớ an toàn**: Tự động dọn dẹp các tiến trình `EXCEL.EXE` chạy ngầm, giải phóng RAM sau mỗi file và dọn dẹp thư mục tạm an toàn.

---

## 🏗️ Kiến trúc Tổng quan (Clean Architecture)

```mermaid
graph TD
    A[main.py] --> B[ui/main_window_modern.py]
    B --> C[core/comparator.py]
    
    subgraph "Core Business Logic"
        C --> D[Strategy A: PDF Workflow]
        C --> E[Strategy B: Legacy Screenshot Workflow]
    end
    
    subgraph "Service Layer"
        D --> F[services/pdf_service.py]
        D --> G[services/optimized_image_compare.py]
        E --> H[services/legacy_screenshot_service.py]
        E --> G
        C --> I[services/excel_service.py]
        C --> J[services/report_service.py]
        C --> K[services/cleanup_service.py]
        B --> L[services/settings_service.py]
        B --> M[services/update_service.py]
        B --> N[services/release_update_service.py]
        B --> O[services/validation_service.py]
    end

    subgraph "UI & Localization"
        B --> P[ui/translations.py (VI/EN/ZH/JA)]
        B --> Q[ui/modern_style.py]
        B --> R[ui/help_window.py]
    end
```

---

## 📁 Cấu trúc Thư mục

```text
Refactored/
├── main.py                          # Điểm khởi chạy ứng dụng chính
├── config.py                        # Cấu hình hằng số hệ thống, màu sắc, DPI, đường dẫn
├── utils.py                         # Tiện ích chung: xử lý file, Windows COM, logging UTF-8
├── run_tests.py                     # Trình chạy toàn bộ 66 Unit Test tự động
├── benchmark_performance.py         # Script benchmark đo đạc hiệu năng CPU/RAM
├── package_app.py                   # Script đóng gói ứng dụng (PyInstaller / Inno Setup)
│
├── core/                            # Tầng lõi nghiệp vụ
│   └── comparator.py                # Bộ điều phối so sánh trung tâm (Strategy Router)
│
├── services/                        # Tầng dịch vụ chuyên biệt (Service Layer)
│   ├── excel_service.py             # Quản lý COM Excel, tiền xử lý sheet, unblock file
│   ├── pdf_service.py               # Xuất Excel sang PDF, render ảnh PyMuPDF, gộp PDF
│   ├── optimized_image_compare.py   # Thuật toán so sánh ảnh OpenCV & PIL fallback
│   ├── report_service.py            # Tạo file Excel kết quả & chèn ảnh side-by-side
│   ├── screenshot_service.py        # Dịch vụ chụp ảnh màn hình Excel
│   ├── legacy_screenshot_service.py # Port logic chụp ảnh Cut/Paste từ bản legacy
│   ├── cleanup_service.py           # Dọn dẹp file tạm, thư mục kết quả cũ, giải phóng RAM
│   ├── settings_service.py          # Lưu trữ và tải cấu hình người dùng (user_settings.json)
│   ├── update_service.py            # Kiểm tra cập nhật qua GitHub / Local Catalog
│   ├── release_update_service.py    # Tải và xác thực bộ cài Inno Setup an toàn
│   ├── help_service.py              # Dịch vụ hướng dẫn sử dụng & trạng thái thư viện
│   └── validation_service.py        # Kiểm tra tính hợp lệ của file và cấu trúc OpenXML
│
├── ui/                              # Giao diện người dùng Tkinter
│   ├── main_window_modern.py        # Cửa sổ chính hiện đại (Modern GUI, 5-step workflow)
│   ├── main_window.py               # Cửa sổ chính giao diện cổ điển
│   ├── modern_style.py              # Hệ thống style, màu sắc, bo góc, card layout
│   ├── translations.py              # Từ điển dịch thuật 4 ngôn ngữ (vi, en, zh, ja)
│   ├── ui_utils.py                  # Widgets bổ trợ: ToolTip, DragDropListbox, StatusBar
│   └── help_window.py               # Cửa sổ hướng dẫn chi tiết 5 tab đa ngôn ngữ
│
├── installer/                       # Cấu hình đóng gói cài đặt
│   └── build_installer.ps1          # Kịch bản build file cài đặt Windows
│
├── docs/                            # Tài liệu dự án chi tiết
│   ├── USER_GUIDE.md                # Cẩm nang hướng dẫn sử dụng cho người dùng cuối
│   ├── TECHNICAL_SPEC.md            # Đặc tả kỹ thuật & giải thuật nội bộ
│   └── reports/                     # Các báo cáo nghiệm thu & audit hiệu năng
│
└── tests/                           # Bộ kiểm thử tự động (66 unit tests)
    ├── test_comparator.py           # Kiểm thử bộ so sánh ảnh & Comparator
    ├── test_doc_modes.py            # Kiểm thử xác thực cấu trúc 3 chế độ tài liệu
    ├── test_excel_service.py        # Kiểm thử tiền xử lý sheet & auto_add_b
    ├── test_file_selection.py       # Kiểm thử logic chọn file và deduplication
    ├── test_legacy_screenshot.py    # Kiểm thử phương pháp chụp màn hình legacy
    ├── test_pdf_fix_and_logging.py  # Kiểm thử sanitize filename & UTF-8 logging
    ├── test_performance_fixes.py   # Kiểm thử giải phóng bộ nhớ & các tối ưu
    ├── test_release_update_service.py # Kiểm thử xác thực và tải bản cập nhật
    ├── test_translations_and_errors.py # Kiểm thử độ phủ từ điển và thông báo lỗi
    └── test_ui_busy_state.py        # Kiểm thử trạng thái khóa nút và bảo vệ UI
```

---

## 🚀 Cài đặt & Hướng dẫn Sử dụng

### 1. Yêu cầu Hệ thống
- **Hệ điều hành**: Windows 10 / 11 hoặc Windows Server (Khuyên dùng Windows có cài sẵn Microsoft Excel 2016/2019/2021/365).
- **Python**: Python 3.9 trở lên (Khuyên dùng Python 3.11 hoặc 3.13).

### 2. Cài đặt các thư viện phụ thuộc
Mở terminal PowerShell tại thư mục dự án và chạy:
```powershell
pip install -r requirements.txt
# Hoặc cài đặt các thư viện nòng cốt:
pip install pywin32 pywinauto Pillow PyMuPDF opencv-python reportlab openpyxl
```

### 3. Khởi chạy ứng dụng
```powershell
python main.py
```

### 4. Quy trình thao tác 5 bước chuẩn hóa:
1. **Bước 1 — Chọn loại tài liệu**: Chọn 1 trong 3 loại tài liệu (*CTTT thông thường*, *CTTT thuộc Tờ Phát Hành ĐƯKC*, hoặc *Tờ Phát Hành ĐƯKC & Khác*) để mở khóa bước chọn file.
2. **Bước 2 — Chọn CTTT mới**: Nhấn nút `📂 Chọn CTTT Mới...` để nạp danh sách file phiên bản mới (hỗ trợ bổ sung hoặc thay thế).
3. **Bước 3 — Chọn CTTT cũ**: Nhấn nút `📂 Chọn CTTT Cũ...` để nạp danh sách file phiên bản cũ tương ứng.
4. **Bước 4 — Kiểm tra & Xác nhận thứ tự**: Nhấn nút `🔍 Kiểm tra & Sắp xếp thứ tự các cặp CTTT` để đối chiếu từng cặp, kéo thả điều chỉnh thứ tự, thêm/xóa file nếu số lượng chưa khớp, rồi nhấn `💾 Xác nhận & Lưu thứ tự`.
5. **Bước 5 — Bắt đầu so sánh**: Nhấn nút màu xanh lớn `🚀 BẮT ĐẦU SO SÁNH` (phương pháp PDF khuyên dùng) hoặc nút màu vàng dự phòng để hệ thống tự động xử lý.

---

## 🧪 Chạy Kiểm Thử Tự Động (Automated Testing)

Dự án đi kèm bộ **66 Unit Tests** kiểm thử toàn diện tất cả các trường hợp biên, tiền xử lý tên sheet, lọc màu tab xanh, kiểm tra OpenXML, xác thực đa ngôn ngữ, và thuật toán so sánh ảnh:

```powershell
py run_tests.py
# Hoặc chạy thông qua unittest discover:
py -m unittest discover -s tests -p "test_*.py"
```

**Kết quả kiểm thử:**
```text
Ran 66 tests in 2.488s
OK (100% Passed)
```

---

## 📚 Tài liệu Liên quan
- 📖 [ARCHITECTURE.md](file:///d:/Sandbox/Sosanh_CTTT_cu_moi/Refactored/ARCHITECTURE.md) - Tài liệu thiết kế kiến trúc hệ thống chi tiết
- 💻 [CODEBASE.md](file:///d:/Sandbox/Sosanh_CTTT_cu_moi/Refactored/CODEBASE.md) - Danh mục module, hàm và quan hệ phụ thuộc
- 👤 [docs/USER_GUIDE.md](file:///d:/Sandbox/Sosanh_CTTT_cu_moi/Refactored/docs/USER_GUIDE.md) - Hướng dẫn sử dụng chi tiết từng chức năng cho người dùng
- 🔧 [docs/TECHNICAL_SPEC.md](file:///d:/Sandbox/Sosanh_CTTT_cu_moi/Refactored/docs/TECHNICAL_SPEC.md) - Đặc tả kỹ thuật giải thuật và các quyết định thiết kế
- 📝 [CHANGELOG.md](file:///d:/Sandbox/Sosanh_CTTT_cu_moi/Refactored/CHANGELOG.md) - Lịch sử cập nhật và nâng cấp phần mềm

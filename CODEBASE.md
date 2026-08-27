# 💻 CODEBASE.md - Bản Đồ Mã Nguồn & Danh Mục Module

> **Bản đồ mã nguồn chi tiết, danh mục hàm/lớp và ma trận phụ thuộc giữa các thành phần của hệ thống So sánh CTTT.**

---

## 1. Danh Sách Các God Nodes & Core Abstractions (Từ Graphify)

Theo kết quả phân tích đồ thị tri thức mã nguồn (**Graphify Knowledge Graph** - 629 nodes, 979 edges):

| Node / Lớp | Số lượng liên kết (Edges) | Vị trí định nghĩa | Trách nhiệm chính |
|---|---|---|---|
| [`MainWindow`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/ui/main_window_modern.py) | **45** | `ui/main_window_modern.py` | Quản lý vòng đời UI, xử lý tương tác người dùng, điều phối luồng nền (`Thread`). |
| [`PDFService`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/pdf_service.py) | **30** | `services/pdf_service.py` | Xuất Excel sang PDF qua COM, render trang sang ảnh, gộp PDF. |
| [`ExcelService`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/excel_service.py) | **26** | `services/excel_service.py` | Giao tiếp COM với Excel, chuẩn hóa tên sheet, lọc sheet tab xanh, unblock file. |
| [`Comparator`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/core/comparator.py) | **25** | `core/comparator.py` | Bộ điều phối logic so sánh chính (Router cho Strategy PDF và Screenshot). |
| [`LegacyScreenshotService`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/legacy_screenshot_service.py) | **25** | `services/legacy_screenshot_service.py` | Mô phỏng logic chụp ảnh Cut/Paste vùng `EX:GR` từ phiên bản v7.03. |
| [`ToolTip`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/ui/ui_utils.py) | **17** | `ui/ui_utils.py` | Hiển thị gợi ý khi di chuột lên các nút bấm và ô nhập liệu. |
| [`ReportService`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/report_service.py) | **15** | `services/report_service.py` | Tạo bảng tính Excel kết quả và chèn ảnh side-by-side. |

---

## 2. Chi Tiết Các Tệp & Danh Mục Hàm (Module Catalog)

### 2.1. Lõi Nghiệp Vụ (`core/`)

#### [`core/comparator.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/core/comparator.py)
- **Lớp `Comparator`**:
  - `__init__(settings=None)`: Khởi tạo comparator với cấu hình người dùng.
  - `start_comparison(new_file_list, old_file_list, status_callback, settings)`: Điểm vào chính để khởi động quá trình so sánh.
  - `_process_legacy_pdf_workflow(new_file_list, old_file_list, output_folder, status_callback)`: Thực thi chiến lược so sánh qua PDF (Strategy A) với đa luồng `ThreadPoolExecutor`.
  - `_process_screenshot_workflow(new_files, old_files, output_folder, status_callback)`: Thực thi chiến lược so sánh qua Screenshot (Strategy B).
  - `_capture_sheets_to_images(...)`: Chụp ảnh các sheet từ file Excel tạm.

---

### 2.2. Tầng Dịch Vụ (`services/`)

#### [`services/optimized_image_compare.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/optimized_image_compare.py)
- `compare_images_opencv(img_new, img_old, diff_threshold=40, dilate_size=3, dilate_iterations=2, highlight_color="#ff0000", fill_opacity=40)`:
  - **Mục đích**: So sánh 2 ảnh PIL bằng OpenCV (`cv2.absdiff`).
  - **Đầu ra**: `(left_pil, right_pil, has_diff, diff_pixels_count)`.
- `compare_images_pil(...)`: Phương thức fallback thuần PIL khi không có OpenCV.
- `create_side_by_side(left_img, right_img)`: Ghép ảnh cũ và mới thành 1 ảnh đôi.
- `quick_compare_hash(img1, img2)`: Kiểm tra nhanh 2 ảnh có giống nhau 100% không (dùng `np.array_equal`).

#### [`services/excel_service.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/excel_service.py)
- **Lớp `ExcelService`**:
  - `_init_excel(visible=False)`: Khởi tạo ứng dụng Excel COM an toàn.
  - `open_workbook(file_path, read_only=False)`: Mở workbook với cơ chế thử lại (retry).
  - `standard_preprocess(file_path, is_new=True, auto_add_b=False, new_sheet_names_ref=None)`: Tiền xử lý file và tên sheet, lọc sheet màu xanh và đổi font `EX:ZZ`.
  - `_make_unique_sheet_name(workbook, base_name)`: Đảm bảo tên sheet không trùng lặp và không vượt quá 31 ký tự.
  - `cleanup()`: Đóng Excel và giải phóng tiến trình.

#### [`services/pdf_service.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/pdf_service.py)
- **Lớp `PDFService`**:
  - `get_colored_sheets(excel_path)`: Lấy danh sách tên các sheet có màu tab xanh (`5296274`).
  - `export_sheets_to_pdf_with_retry(excel_path, sheet_names, output_pdf_path)`: Xuất các sheet được chỉ định ra PDF.
  - `_export_pdf_fallback(excel_path, sheet_names, output_pdf_path)`: Phương pháp sao chép từng sheet sang workbook mới để xuất PDF (bảo toàn thứ tự sheet chuẩn xác).
  - `render_pdf_to_images(pdf_path, dpi=100)`: Render toàn bộ các trang của file PDF thành danh sách PIL Image.
  - `merge_pdfs(pdf_list, output_path)`: Gộp danh sách các file PDF thành 1 file duy nhất.

#### [`services/report_service.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/report_service.py)
- **Lớp `ReportService`**:
  - `add_result(file_name, sheet_name, status, message, image_path=None)`: Thêm bản ghi kết quả.
  - `create_per_file_excel_result(new_file_path, comparison_images, old_images, output_folder, is_pdf_method, dpi)`: Tạo file Excel kết quả chứa ảnh so sánh.

#### [`services/cleanup_service.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/services/cleanup_service.py)
- **Lớp `CleanupService`**:
  - `cleanup_temp_images(base_path, keep_diff_images=True)`: Dọn dẹp ảnh tạm.
  - `cleanup_old_results(base_path, keep_latest_n=5)`: Dọn dẹp các thư mục kết quả cũ.
  - `full_cleanup(base_path)`: Dọn dẹp toàn diện.

---

### 2.3. Tầng Giao Diện Người Dùng (`ui/`)

- [`ui/main_window_modern.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/ui/main_window_modern.py): Giao diện Tkinter hiện đại, chứa thanh menu, card chọn file, card cài đặt nâng cao, thanh tiến trình và các nút điều khiển.
- [`ui/modern_style.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/ui/modern_style.py): Cấu hình TTk Style, bảng màu `MODERN_COLORS`.
- [`ui/translations.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/ui/translations.py): Từ điển đa ngôn ngữ (Tiếng Việt / English).
- [`ui/ui_utils.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/ui/ui_utils.py): `ToolTip`, `FilePairListbox`, `DragDropListbox`, `StatusBar`.
- [`ui/help_window.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/ui/help_window.py): Cửa sổ Trợ giúp & Giới thiệu.

---

### 2.4. Tiện Ích & Cấu Hình (`utils.py`, `config.py`)

- [`config.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/config.py):
  - Hằng số màu tab xanh: `COLOR_GREEN_TAB = 5296274`.
  - Tham số mặc định: `DEFAULT_DPI = 100`, `DEFAULT_DIFF_THRESHOLD = 40`, `DEFAULT_FILL_OPACITY = 40`.
- [`utils.py`](file:///d:/Sandbox/pmsosanhCTTT/Refactored%20so%20s%C3%A1nh%20CTTT%20c%C5%A9%20m%E1%BB%9Bi/Refactored/utils.py):
  - Cấu hình Unicode StreamHandler UTF-8 an toàn trên Windows.
  - `safe_rename_file(file_path)`: Đổi tên file loại bỏ ký tự nhạy cảm.
  - `unblock_file(file_path)`: Gỡ cờ Zone.Identifier (Mark of the Web) trên Windows PowerShell.
  - `kill_specific_excel_process(pid)`: Tiêu diệt tiến trình Excel cụ thể dựa trên PID.

---

## 3. Ma Trận Phụ Thuộc Tệp (File Dependency Matrix)

| Tệp (Source) | Phụ thuộc vào các tệp (Dependencies) |
|---|---|
| `main.py` | `ui/main_window_modern.py`, `config.py`, `utils.py` |
| `ui/main_window_modern.py` | `core/comparator.py`, `services/*`, `ui/modern_style.py`, `ui/translations.py`, `ui/ui_utils.py` |
| `core/comparator.py` | `services/excel_service.py`, `services/pdf_service.py`, `services/optimized_image_compare.py`, `services/report_service.py`, `services/cleanup_service.py`, `config.py`, `utils.py` |
| `services/excel_service.py` | `config.py`, `utils.py` |
| `services/pdf_service.py` | `services/excel_service.py`, `config.py`, `utils.py` |
| `services/optimized_image_compare.py` | `utils.py` |
| `services/report_service.py` | `services/excel_service.py`, `config.py`, `utils.py` |
| `services/legacy_screenshot_service.py`| `config.py`, `utils.py` |

# Graph Report - .  (2026-08-26)

## Corpus Check
- Corpus is ~38,824 words - fits in a single context window. You may not need a graph.

## Summary
- 629 nodes · 979 edges · 41 communities (32 shown, 9 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 46 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Modern Tkinter UI & Theme
- Modern Tkinter UI & Theme
- Comparison Engine & Image Diffing
- Excel COM & Preprocessing
- Community 4 Components
- Modern Tkinter UI & Theme
- Excel COM & Preprocessing
- Comparison Engine & Image Diffing
- Comparison Engine & Image Diffing
- Modern Tkinter UI & Theme
- Modern Tkinter UI & Theme
- Excel COM & Preprocessing
- Comparison Engine & Image Diffing
- Modern Tkinter UI & Theme
- Comparison Engine & Image Diffing
- Comparison Engine & Image Diffing
- Comparison Engine & Image Diffing
- Modern Tkinter UI & Theme
- Excel COM & Preprocessing
- Modern Tkinter UI & Theme
- Modern Tkinter UI & Theme
- Modern Tkinter UI & Theme
- Excel COM & Preprocessing
- Modern Tkinter UI & Theme
- Utilities & Configuration
- Comparison Engine & Image Diffing
- Reporting & Memory Cleanup
- Modern Tkinter UI & Theme
- Modern Tkinter UI & Theme
- Modern Tkinter UI & Theme
- PDF Service & PageSetup
- Modern Tkinter UI & Theme
- Comparison Engine & Image Diffing
- PDF Service & PageSetup
- Excel COM & Preprocessing
- Excel COM & Preprocessing
- Modern Tkinter UI & Theme
- Modern Tkinter UI & Theme
- Modern Tkinter UI & Theme

## God Nodes (most connected - your core abstractions)
1. `MainWindow` - 45 edges
2. `MainWindow` - 43 edges
3. `PDFService` - 30 edges
4. `ExcelService` - 26 edges
5. `Comparator` - 25 edges
6. `LegacyScreenshotService` - 25 edges
7. `ToolTip` - 17 edges
8. `ModernHelpWindow` - 16 edges
9. `get_text()` - 16 edges
10. `ReportService` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Comparator` --uses--> `CleanupService`  [INFERRED]
  core/comparator.py → services/cleanup_service.py
- `Comparator` --uses--> `ExcelService`  [INFERRED]
  core/comparator.py → services/excel_service.py
- `Comparator` --uses--> `LegacyScreenshotService`  [INFERRED]
  core/comparator.py → services/legacy_screenshot_service.py
- `Comparator` --uses--> `PDFService`  [INFERRED]
  core/comparator.py → services/pdf_service.py
- `Comparator` --uses--> `ReportService`  [INFERRED]
  core/comparator.py → services/report_service.py

## Import Cycles
- None detected.

## Communities (41 total, 9 thin omitted)

### Community 0 - "Modern Tkinter UI & Theme"
Cohesion: 0.06
Nodes (21): main(), MainWindow, Khởi tạo và cập nhật thanh menu đa ngôn ngữ, Hiển thị danh sách phím tắt, Gắn phím tắt cho các chức năng chính, Mở thư mục kết quả trong Explorer, Kiểm tra phiên bản mới từ server, Hiển thị hộp thoại xác nhận thứ tự các cặp file CTTT để người dùng kiểm tra và… (+13 more)

### Community 1 - "Modern Tkinter UI & Theme"
Cohesion: 0.05
Nodes (23): DragDropListbox, FilePairListbox, ProgressDialog, UI Utilities - Các widget và helper UI Bao gồm: - ToolTip: Hiển thị tooltip khi…, Trong quá trình drag., Thanh trạng thái đơn giản. Sử dụng: status = StatusBar(parent)…, Tạo tooltip hover cho các widget. Sử dụng: tooltip = ToolTip(button, "Nội dung…, Cập nhật nội dung status bar. (+15 more)

### Community 2 - "Comparison Engine & Image Diffing"
Cohesion: 0.06
Nodes (22): Phương pháp Legacy Screenshot - Mô phỏng thao tác người dùng từ phiên bản cũ.…, LegacyScreenshotService, Legacy Screenshot Service - Mô phỏng phương pháp chụp ảnh từ phiên bản cũ Port…, Tạo tên sheet duy nhất để tránh trùng lặp, Mở file Excel và trả về đối tượng Excel và workbook (Legacy method), Kết nối với cửa sổ Excel (Legacy method), Đóng Excel và giải phóng tài nguyên, Tắt gridlines trong Excel (+14 more)

### Community 3 - "Excel COM & Preprocessing"
Cohesion: 0.06
Nodes (20): ExcelService, Creates a new workbook., Quits Excel and ensures process cleanup., Copies range directly without Clipboard using Range.Copy destination. Preserves…, Applies specific row heights as per requirements., Exports workbook to PDF with retry logic and permission handling., Initializes Excel Application safely with retry and fallback logic., Tạo tên sheet duy nhất và đảm bảo không quá 31 ký tự. Args: workbook: COM… (+12 more)

### Community 4 - "Community 4 Components"
Cohesion: 0.07
Nodes (17): MessageHandler, Validation Service - Kiểm tra và xác thực dữ liệu đầu vào Bao gồm: - Validation…, Validate dilate size (1-9, odd number)., Validate dilate iterations (1-3)., Validate opacity percentage (0-100)., Validate hex color code., Service validation và message handling., Validate Excel file. Returns: Tuple (is_valid, error_message) (+9 more)

### Community 5 - "Modern Tkinter UI & Theme"
Cohesion: 0.09
Nodes (16): HelpService, Help Service - Hướng dẫn sử dụng và thông tin ứng dụng, Service hiển thị hướng dẫn và thông tin ứng dụng., Hiển thị hướng dẫn sử dụng. Args: parent: Parent window (tkinter) detailed: Nếu…, Hiển thị thông tin ứng dụng., Hiển thị các phím tắt., Hiển thị trạng thái các thư viện., LibraryValidator (+8 more)

### Community 6 - "Excel COM & Preprocessing"
Cohesion: 0.08
Nodes (24): format_file_size(), get_excel_pid(), get_safe_write_path(), get_writable_dir(), is_file_locked(), kill_specific_excel_process(), Checks if a path is writable, otherwise falls back to Documents or Temp., Renames file replacing special chars with hyphens. (+16 more)

### Community 7 - "Comparison Engine & Image Diffing"
Cohesion: 0.11
Nodes (12): Main entry point for comparison process. status_callback: function(msg) to…, CleanupService, Cleanup Service - Quản lý file tạm và dọn dẹp Ported từ Legacy SosanhCTTT để…, Xóa các file ảnh tạm trong quá trình xử lý. Args: base_path: Đường dẫn thư mục…, Service quản lý cleanup cho: - Thư mục tạm (tmp*) - File Excel tạm…, Thực hiện dọn dẹp toàn diện. Args: base_path: Đường dẫn thư mục cần dọn…, Xóa các thư mục kết quả cũ, chỉ giữ lại một số folder gần nhất. Args:…, Tạo thư mục tạm trong base_path. Args: base_path: Đường dẫn thư mục cha… (+4 more)

### Community 8 - "Comparison Engine & Image Diffing"
Cohesion: 0.13
Nodes (15): check_for_update(), compare_versions(), get_current_version(), perform_update(), Auto Update Service - Tự động cập nhật phần mềm từ server Triển khai ngang từ…, Helper class để tích hợp với Tkinter UI, Args: master: Tkinter root window on_update_available: Callback khi có update,…, Kiểm tra update sau delay_ms mili giây (+7 more)

### Community 9 - "Modern Tkinter UI & Theme"
Cohesion: 0.12
Nodes (19): create_card_frame(), create_modern_button(), create_section_header(), create_status_bar(), darken_color(), hex_to_rgb(), lighten_color(), Modern UI Style Configuration Thiết kế hiện đại, chuyên nghiệp và tối giản (+11 more)

### Community 10 - "Modern Tkinter UI & Theme"
Cohesion: 0.15
Nodes (13): _get_date_from_exe(), _get_version_from_exe(), Tự động lấy ngày từ modification time của file .exe Hoặc lấy ngày hiện tại nếu…, Tự động lấy version từ tên file .exe đang chạy Ví dụ:…, main(), Modern Main Window UI Giao diện hiện đại, chuyên nghiệp và tối giản, Colors, Spacing và padding values (+5 more)

### Community 11 - "Excel COM & Preprocessing"
Cohesion: 0.15
Nodes (10): Thêm một sheet mới với kết quả so sánh (embedded image hoặc hyperlink). Args:…, Chèn preview của trang đầu PDF vào worksheet., Chèn ảnh vào worksheet., Thêm hyperlink đến file., Tạo báo cáo nhiều sheet từ danh sách kết quả so sánh PDF. Args:…, Service tạo báo cáo Excel với kết quả so sánh., Lưu file báo cáo. Args: filename: Tên file báo cáo Returns: Đường dẫn file nếu…, Khởi tạo header cho sheet tổng hợp. (+2 more)

### Community 12 - "Comparison Engine & Image Diffing"
Cohesion: 0.24
Nodes (12): STRATEGY B: Screenshot Comparison Workflow Logic: 1. Mở từng cặp file Excel…, compare_images_opencv(), compare_images_pil(), create_side_by_side(), is_opencv_available(), quick_compare_hash(), Optimized Image Comparison Service using OpenCV Tối ưu hóa hiệu suất xử lý ảnh:…, Fallback: So sánh ảnh sử dụng PIL (khi không có OpenCV). Returns: Tuple… (+4 more)

### Community 13 - "Modern Tkinter UI & Theme"
Cohesion: 0.14
Nodes (7): MainWindow, Hiển thị danh sách phím tắt, Thread chạy Legacy comparison, Tạo và hiển thị thanh tiến trình và label trạng thái, Cập nhật giá trị thanh tiến trình và label phần trăm, Tạo menu bar với các menu File, View, Help, Reset tất cả cài đặt về mặc định

### Community 14 - "Comparison Engine & Image Diffing"
Cohesion: 0.13
Nodes (9): Chụp ảnh các sheet từ file Excel theo logic legacy: 1. Mở file gốc 2. Tạo…, Screenshot Service - Chụp ảnh màn hình từ Excel Ported từ Legacy SosanhCTTT cho…, Chụp ảnh từ sheet trong file Excel tạm. Tương thích với legacy…, Chụp ảnh một vùng cụ thể trong sheet. Args: excel_app: Excel COM app sheet:…, So sánh 2 screenshot và tạo ảnh diff. Args: img_path1: Đường dẫn ảnh 1…, Service chụp ảnh màn hình từ Excel sheets. Dùng cho workflow so sánh bằng hình…, Kiểm tra thư viện screenshot có sẵn không., Chụp ảnh màn hình từ một sheet Excel. Args: excel_app: Excel COM application… (+1 more)

### Community 15 - "Comparison Engine & Image Diffing"
Cohesion: 0.12
Nodes (8): PDFService, Comprehensive PDF Service for: - Exporting Excel sheets to PDF - Merging…, Render a single PDF page to PIL Image. Args: pdf_path: Path to PDF file…, Check which PDF libraries are available. Returns dict with availability status…, Create landscape PDF from image using reportlab., Convert hex color + opacity to RGBA tuple., Exports a specific sheet to PDF (legacy compatibility)., Tìm tất cả file comparison_*.pdf và ảnh comparison_*.png/jpg, gộp chúng thành…

### Community 16 - "Comparison Engine & Image Diffing"
Cohesion: 0.14
Nodes (8): Comparator, Copies matching sheets from New/Old pairs into wb_merged. Appends context to…, Test that Comparator initializes correctly and has expected attributes, Test comparing identical images reports has_diff = False, Test comparing different images reports has_diff = True with pixel count, Test PIL fallback comparison logic, Test side by side image creation, TestComparator

### Community 17 - "Modern Tkinter UI & Theme"
Cohesion: 0.13
Nodes (7): Mở color chooser để chọn màu nền highlight và cập nhật label, Mở color chooser để chọn màu viền highlight và cập nhật label, Mở color chooser để chọn màu tô highlight và cập nhật label, Validation cho DPI input - đảm bảo giá trị trong khoảng 50-300, Xử lý sự kiện thay đổi chế độ màn hình và cập nhật zoom level tương ứng, Tự động lưu cài đặt nếu checkbox lưu cài đặt được bật, Xử lý khi đóng ứng dụng

### Community 18 - "Excel COM & Preprocessing"
Cohesion: 0.18
Nodes (7): patch, Excel app should start as None, _init_excel() should create excel_app, _init_excel() called twice should not create duplicate instance, _cleanup_excel() should reset excel_app to None, _export_pdf_fallback should reuse self.excel_app when available, TestPDFServiceKeepAlive

### Community 19 - "Modern Tkinter UI & Theme"
Cohesion: 0.42
Nodes (3): ModernHelpWindow, Create a tab frame with a scrollbar, Load and display an image from assets/help

### Community 20 - "Modern Tkinter UI & Theme"
Cohesion: 0.25
Nodes (10): benchmark_opencv_method(), benchmark_pil_method(), benchmark_quick_hash(), create_test_images(), main(), Benchmark Script: So sanh hieu suat PIL vs OpenCV Script nay tao 2 anh gia lap…, Benchmark phương pháp OpenCV tối ưu, Benchmark quick hash comparison (+2 more)

### Community 21 - "Modern Tkinter UI & Theme"
Cohesion: 0.29
Nodes (3): object, create a tooltip for a given widget, ToolTip

### Community 22 - "Excel COM & Preprocessing"
Cohesion: 0.22
Nodes (5): Cleanup Excel COM application., Export specified sheets from Excel file to a single PDF. Args: file_path: Path…, Export sheets to PDF with retry mechanism and fallback. Matches legacy…, Fallback method: Copy sheets to new workbook and export from there. This…, Merge multiple PDF files into one. Args: pdf_list: List of PDF file paths to…

### Community 23 - "Modern Tkinter UI & Theme"
Cohesion: 0.20
Nodes (3): Chạy phương pháp Legacy Screenshot (giống phiên bản cũ), Gắn phím tắt cho các chức năng chính, Mở thư mục kết quả trong Explorer

### Community 24 - "Utilities & Configuration"
Cohesion: 0.31
Nodes (4): Determines the correct path for the settings file (EXE vs Script)., Loads settings from JSON file or returns defaults., Saves current settings to JSON if 'save_settings' is True., SettingsService

### Community 25 - "Comparison Engine & Image Diffing"
Cohesion: 0.32
Nodes (4): ImageComparisonService, Chuyển mã màu hex và độ mờ thành tuple RGBA, Post-processes the difference image to add red highlights., Compares two images and saves the difference image with highlights. Args:…

### Community 26 - "Reporting & Memory Cleanup"
Cohesion: 0.25
Nodes (5): Integration Tests for Performance Fixes Tests 6 fixes applied after the…, Verify del correctly removes reference (Python GC test), config.DEFAULT_ZOOM should exist and be a valid number, TestMemoryCleanup, TestZoomConfig

### Community 27 - "Modern Tkinter UI & Theme"
Cohesion: 0.25
Nodes (3): Hiển thị dialog kiểm tra và sắp xếp thứ tự file, Hiển thị hộp thoại xác nhận thứ tự các cặp file CTTT, Enable drag and drop reordering for a listbox

### Community 30 - "PDF Service & PageSetup"
Cohesion: 0.33
Nodes (3): Test logic làm sạch tên file nghiêm ngặt, Test initialization of hidden logging, TestPdfFixAndLogging

### Community 31 - "Modern Tkinter UI & Theme"
Cohesion: 0.40
Nodes (3): configure_styles(), Fonts, Áp dụng ttk styling hiện đại cho toàn bộ ứng dụng. Call function này ngay sau…

## Knowledge Gaps
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Comparator` connect `Comparison Engine & Image Diffing` to `Comparison Engine & Image Diffing`, `Modern Tkinter UI & Theme`, `Comparison Engine & Image Diffing`, `Excel COM & Preprocessing`, `Comparison Engine & Image Diffing`, `Modern Tkinter UI & Theme`, `Excel COM & Preprocessing`, `Comparison Engine & Image Diffing`, `Modern Tkinter UI & Theme`, `Comparison Engine & Image Diffing`, `Comparison Engine & Image Diffing`, `Modern Tkinter UI & Theme`, `Modern Tkinter UI & Theme`?**
  _High betweenness centrality (0.318) - this node is a cross-community bridge._
- **Why does `MainWindow` connect `Modern Tkinter UI & Theme` to `Modern Tkinter UI & Theme`, `Modern Tkinter UI & Theme`, `Modern Tkinter UI & Theme`, `Modern Tkinter UI & Theme`, `Modern Tkinter UI & Theme`, `Comparison Engine & Image Diffing`, `Modern Tkinter UI & Theme`, `Modern Tkinter UI & Theme`, `Utilities & Configuration`, `Modern Tkinter UI & Theme`, `Modern Tkinter UI & Theme`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Why does `PDFService` connect `Comparison Engine & Image Diffing` to `PDF Service & PageSetup`, `Excel COM & Preprocessing`, `Excel COM & Preprocessing`, `Excel COM & Preprocessing`, `Comparison Engine & Image Diffing`, `Comparison Engine & Image Diffing`, `Excel COM & Preprocessing`, `Excel COM & Preprocessing`, `Reporting & Memory Cleanup`, `Modern Tkinter UI & Theme`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `MainWindow` (e.g. with `Comparator` and `HelpService`) actually correct?**
  _`MainWindow` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `MainWindow` (e.g. with `Comparator` and `SettingsService`) actually correct?**
  _`MainWindow` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `PDFService` (e.g. with `Comparator` and `TestExcelServiceFixes`) actually correct?**
  _`PDFService` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ExcelService` (e.g. with `Comparator` and `TestExcelService`) actually correct?**
  _`ExcelService` has 8 INFERRED edges - model-reasoned connections that need verification._
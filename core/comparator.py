import os
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from services.excel_service import ExcelService
from services.pdf_service import PDFService
from services.cleanup_service import CleanupService
import config
import utils

# Import optimized image comparison
try:
    from services.optimized_image_compare import (
        compare_images_opencv, create_side_by_side, quick_compare_hash, is_opencv_available
    )
    OPENCV_AVAILABLE = is_opencv_available()
except ImportError:
    OPENCV_AVAILABLE = False
    compare_images_opencv = None
    create_side_by_side = None
    quick_compare_hash = None

class Comparator:
    def __init__(self, use_pdf_method=False):
        self.use_pdf_method = use_pdf_method
        self.excel_service = None
        self.pdf_service = PDFService()

    def start_legacy_comparison(self, new_file_list, old_file_list, status_callback=None, 
                                  progress_callback=None, settings=None):
        """
        Phương pháp Legacy Screenshot - Mô phỏng thao tác người dùng từ phiên bản cũ.
        
        Khác với phương pháp Screenshot hiện tại:
        - Mở Excel trực tiếp (visible) trên màn hình
        - Chụp ảnh từ màn hình thực tế (không qua temp workbook)
        - Hỗ trợ nhiều chế độ màn hình (PC, VPS, Monitor phụ)
        - Tiền xử lý file (ẩn cột, đồng bộ độ rộng cột)
        
        Args:
            new_file_list: Danh sách file CTTT mới
            old_file_list: Danh sách file CTTT cũ
            status_callback: Hàm callback cập nhật trạng thái
            progress_callback: Hàm callback cập nhật tiến độ (0-100)
            settings: Dict cấu hình
            
        Returns:
            Elapsed time in seconds
        """
        from services.legacy_screenshot_service import LegacyScreenshotService
        
        if len(new_file_list) != len(old_file_list):
            raise ValueError("File lists must have equal length.")
        
        settings = settings or {}
        
        # Khởi tạo Legacy service
        legacy_service = LegacyScreenshotService()
        
        # Áp dụng cài đặt
        legacy_service.set_screen_mode(settings.get('screen_mode', 'pc'))
        legacy_service.set_zoom_level(settings.get('zoom', config.DEFAULT_ZOOM))
        legacy_service.set_goto_address(settings.get('goto_address', config.DEFAULT_GOTO_ADDRESS))
        legacy_service.set_highlight_settings(
            settings.get('highlight_fill_color', config.HIGHLIGHT_FILL_COLOR),
            settings.get('highlight_fill_opacity', config.DEFAULT_FILL_OPACITY)
        )
        
        # Xác định output folder
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        preferred_folder = settings.get("output_folder", None)
        
        if preferred_folder and os.path.exists(preferred_folder):
            output_folder = os.path.join(preferred_folder, f"{config.DEFAULT_OUTPUT_FOLDER_NAME}_Legacy_{timestamp}")
        else:
            output_folder = utils.get_writable_dir(
                os.path.dirname(new_file_list[0]), 
                f"{config.DEFAULT_OUTPUT_FOLDER_NAME}_Legacy_{timestamp}"
            )
        
        output_folder = os.path.normpath(output_folder)
        os.makedirs(output_folder, exist_ok=True)
        
        utils.logger.info(f"[Legacy] Results will be saved to: {output_folder}")
        
        if status_callback:
            status_callback("[Legacy] Bắt đầu phương pháp Legacy Screenshot...")
        
        # Chạy quy trình Legacy
        success, elapsed_time, results = legacy_service.run_full_comparison(
            new_file_list,
            old_file_list,
            output_folder,
            status_callback,
            progress_callback
        )
        
        if success:
            minutes, seconds = divmod(elapsed_time, 60)
            utils.logger.info(f"[Legacy] Completed in {int(minutes)} phút {seconds:.2f} giây")
            if status_callback:
                status_callback(f"[Legacy] Hoàn tất! Thời gian: {int(minutes)} phút {seconds:.2f} giây")
            
            # Mở folder kết quả
            try:
                os.startfile(output_folder)
            except:
                pass
        
        return elapsed_time

    def start_comparison(self, new_file_list, old_file_list, status_callback=None, settings=None):
        """
        Main entry point for comparison process.
        status_callback: function(msg) to update UI.
        settings: dict of configuration values.
        """
        if len(new_file_list) != len(old_file_list):
            raise ValueError("File lists must have equal length.")
            
        self.settings = settings
        suppress = settings.get("suppress_error", True) if settings else True
        self.excel_service = ExcelService(suppress_alerts=suppress)
        
        # Start timing
        start_time = time.time()
        
        try:
            # --- Preprocessing Phase ---
            if status_callback: status_callback("Preprocessing files...")
            
            processed_new_files = []
            processed_old_files = []
            
            # Preprocess New Files
            new_sheet_names_collection = {} # Map file_idx -> list of (old, new) sheet names
            
            for idx, f_path in enumerate(new_file_list):
                 # For new files, auto_add_b is False
                 proc_path, sheet_names = self.excel_service.standard_preprocess(f_path, auto_add_b=False)
                 processed_new_files.append(proc_path)
                 new_sheet_names_collection[idx] = sheet_names
                 
            # Preprocess Old Files (with 'b' logic)
            for idx, f_path in enumerate(old_file_list):
                # Auto add 'b' if enabled
                do_auto_b = settings.get("auto_add_b", False) if settings else False
                
                # Get reference sheet names from corresponding new file
                ref_names = new_sheet_names_collection.get(idx, [])
                
                proc_path, _ = self.excel_service.standard_preprocess(f_path, auto_add_b=do_auto_b, new_sheet_names_ref=ref_names) 
                processed_old_files.append(proc_path)

            # --- Comparison Phase ---
            # Create Output Folder
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            preferred_folder = settings.get("output_folder", None)
            
            if preferred_folder and os.path.exists(preferred_folder):
                output_folder = os.path.join(preferred_folder, f"{config.DEFAULT_OUTPUT_FOLDER_NAME}_{timestamp}")
            else:
                output_folder = utils.get_writable_dir(os.path.dirname(new_file_list[0]), f"{config.DEFAULT_OUTPUT_FOLDER_NAME}_{timestamp}")
            
            output_folder = os.path.normpath(output_folder)
            os.makedirs(output_folder, exist_ok=True)
            
            utils.logger.info(f"Results will be saved to: {output_folder}")
            
            # Init Report
            from services.report_service import ReportService
            self.report_service = ReportService(output_folder)
            
            # ================================================================
            # STRATEGY PATTERN: PDF Workflow vs Screenshot Workflow
            # ================================================================
            # use_pdf_method = True  → PDF comparison (export to PDF, compare rendered images)
            # use_pdf_method = False → Screenshot comparison (open Excel, take screenshots, compare)
            # ================================================================
            
            if self.use_pdf_method:
                # STRATEGY A: PDF Comparison Workflow
                utils.logger.info("Using PDF comparison workflow")
                if status_callback:
                    status_callback("Đang sử dụng phương pháp PDF...")
                
                self._process_legacy_pdf_workflow(
                    processed_new_files, 
                    processed_old_files, 
                    output_folder, 
                    status_callback
                )
                
                # Cleanup temp files
                if status_callback:
                    status_callback("Dọn dẹp file tạm...")
                CleanupService.cleanup_temp_images(output_folder, keep_diff_images=True)
                CleanupService.cleanup_per_sheet_pdfs(output_folder)
                
            else:
                # STRATEGY B: Screenshot Comparison Workflow
                utils.logger.info("Using Screenshot comparison workflow")
                if status_callback:
                    status_callback("Đang sử dụng phương pháp Screenshot (Cut/Paste)...")
                
                self._process_screenshot_workflow(
                    processed_new_files,
                    processed_old_files,
                    output_folder,
                    status_callback
                )
                
                # Cleanup temp files
                if status_callback:
                    status_callback("Dọn dẹp file tạm...")
                CleanupService.cleanup_temp_images(output_folder, keep_diff_images=True)
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            minutes, seconds = divmod(elapsed_time, 60)
            
            # Per-file results đã được tạo trong workflow
            utils.logger.info(f"Comparison completed in {int(minutes)} phút {seconds:.2f} giây")
            if status_callback: 
                status_callback(f"Hoàn tất! Thời gian: {int(minutes)} phút {seconds:.2f} giây")
            os.startfile(output_folder)
            
            return elapsed_time
                
        except Exception as e:
            utils.logger.error(f"Comparison Error: {e}")
            raise
        finally:
            if self.excel_service:
                self.excel_service.cleanup()

    def _aggregate_file_pair(self, new_path, old_path, wb_merged, meta_list):
        """
        Copies matching sheets from New/Old pairs into wb_merged.
        Appends context to meta_list.
        """
        file_name = os.path.basename(new_path)
        
        # Open
        wb_new = self.excel_service.open_workbook(new_path)
        if not wb_new:
            self.report_service.add_result(file_name, "N/A", "ERROR", "Không thể mở file mới")
            return
        
        wb_old = self.excel_service.open_workbook(old_path)
        if not wb_old:
             self.excel_service.close_workbook(wb_new)
             self.report_service.add_result(file_name, "N/A", "ERROR", "Không thể mở file cũ")
             return

        try:
             for sheet_new in wb_new.Sheets:
                sheet_name = sheet_new.Name
                if sheet_new.Tab.Color != config.COLOR_GREEN_TAB:
                   continue
                
                # Find Match with variants (matching original behavior)
                sheet_old = None
                try:
                    sheet_old = wb_old.Sheets(sheet_name)
                except Exception:
                    # Fallback 1: Try with underscores instead of dashes
                    variant = sheet_name.replace("-", "_")
                    try:
                        sheet_old = wb_old.Sheets(variant)
                        utils.logger.info(f"Found sheet via underscore variant: {variant}")
                    except Exception:
                        # Fallback 2: Try without 'b' prefix (if present)
                        if sheet_name.lower().startswith('b'):
                            variant_no_b = sheet_name[1:]
                            try:
                                sheet_old = wb_old.Sheets(variant_no_b)
                                utils.logger.info(f"Found sheet via b-prefix removal: {variant_no_b}")
                            except Exception:
                                # Fallback 3: Try underscore variant without 'b'
                                try:
                                    sheet_old = wb_old.Sheets(variant_no_b.replace("-", "_"))
                                except Exception:
                                    pass
                
                if sheet_old is None:
                    self.report_service.add_result(file_name, sheet_name, "MISSING", "Không tìm thấy sheet tương ứng ở file cũ")
                    continue
                
                # Found Pair -> Process into Merged WB
                # 1. Copy New Sheet
                # Note: We must use our Direct Copy because regular Sheet.Copy between workbooks can be unstable/slow
                # But creating a new blank sheet and copying range is safer.
                
                # Create holder sheet in Merged
                target_sheet_new = wb_merged.Sheets.Add(After=wb_merged.Sheets(wb_merged.Sheets.Count))
                # Rename unique? Not strictly necessary for PDF export order, but good for debug
                # target_sheet_new.Name = f"N_{len(meta_list)}_{sheet_name}"[:31]
                
                if self.excel_service.copy_range_direct(sheet_new, target_sheet_new):
                    self.excel_service.format_sheet_layout(target_sheet_new)
                
                # 2. Copy Old Sheet
                target_sheet_old = wb_merged.Sheets.Add(After=wb_merged.Sheets(wb_merged.Sheets.Count))
                # target_sheet_old.Name = f"O_{len(meta_list)}_{sheet_name}"[:31]
                
                if self.excel_service.copy_range_direct(sheet_old, target_sheet_old):
                    self.excel_service.format_sheet_layout(target_sheet_old)
                
                # Record Metadata
                meta_list.append({
                    'file': file_name,
                    'sheet': sheet_name
                })
                
        finally:
            self.excel_service.close_workbook(wb_new)
            self.excel_service.close_workbook(wb_old)

    def _process_legacy_pdf_workflow(self, new_file_list, old_file_list, output_folder, status_callback=None):
        """
        Legacy-compatible PDF comparison workflow.
        
        This method replicates the original process_excel_file_pdf_logic behavior:
        1. For each file pair, export colored sheets to separate PDFs
        2. Compare PDFs page-by-page and create highlighted comparison images
        3. Create per-file Excel result with embedded images (Kết quả_PDF_*.xlsx)
        4. Optionally merge all comparison PDFs into final result
        """
        from services.report_service import ReportService
        
        # Get settings
        dpi = self.settings.get('dpi', config.DEFAULT_DPI) if self.settings else config.DEFAULT_DPI
        threshold = self.settings.get('pdf_diff_threshold', config.DEFAULT_DIFF_THRESHOLD) if self.settings else config.DEFAULT_DIFF_THRESHOLD
        highlight_color = self.settings.get('highlight_fill_color', config.HIGHLIGHT_FILL_COLOR) if self.settings else config.HIGHLIGHT_FILL_COLOR
        fill_opacity = self.settings.get('highlight_fill_opacity', config.DEFAULT_FILL_OPACITY) if self.settings else config.DEFAULT_FILL_OPACITY
        dilate_size = self.settings.get('pdf_dilate_size', config.DEFAULT_DILATE_SIZE) if self.settings else config.DEFAULT_DILATE_SIZE
        dilate_iterations = self.settings.get('pdf_dilate_iterations', config.DEFAULT_DILATE_ITERATIONS) if self.settings else config.DEFAULT_DILATE_ITERATIONS
        
        total_files = len(new_file_list)
        all_comparison_pdfs = []  # For final merged PDF
        
        for idx, (new_path, old_path) in enumerate(zip(new_file_list, old_file_list)):
            file_name = os.path.basename(new_path)
            file_comparison_images = {}  # {sheet_name: comparison_img_path}
            file_comparison_pdfs = []
            
            if status_callback:
                status_callback(f"Processing {idx+1}/{total_files}: {file_name}")
            
            try:
                # Step 1: Get colored sheets from NEW file
                colored_sheets = self.pdf_service.get_colored_sheets(new_path)
                
                if not colored_sheets:
                    utils.logger.warning(f"No green-tab sheets found in {file_name}")
                    self.report_service.add_result(file_name, "N/A", "WARNING", "Không tìm thấy sheet màu xanh")
                    continue
                
                # Step 2: Export NEW file sheets to PDF
                if status_callback:
                    status_callback(f"Exporting PDF (NEW): {file_name}")
                    
                pdf_new_path = os.path.join(output_folder, f"CTTTmoi_{idx}.pdf")
                success_new = self.pdf_service.export_sheets_to_pdf_with_retry(new_path, colored_sheets, pdf_new_path)
                
                if not success_new:
                    self.report_service.add_result(file_name, "N/A", "ERROR", "Không xuất được PDF mới")
                    continue
                
                # Step 3: Export OLD file sheets to PDF
                if status_callback:
                    status_callback(f"Exporting PDF (OLD): {os.path.basename(old_path)}")
                    
                pdf_old_path = os.path.join(output_folder, f"CTTTcu_{idx}.pdf")
                success_old = self.pdf_service.export_sheets_to_pdf_with_retry(old_path, colored_sheets, pdf_old_path)
                
                if not success_old:
                    self.report_service.add_result(file_name, "N/A", "ERROR", "Không xuất được PDF cũ")
                    continue
                
                # Step 4: Compare PDFs page by page
                if status_callback:
                    status_callback(f"Comparing: {file_name}")
                
                new_images = self.pdf_service.render_pdf_to_images(pdf_new_path, dpi)
                old_images = self.pdf_service.render_pdf_to_images(pdf_old_path, dpi)
                
                num_pages = min(len(new_images), len(old_images))
                
                # === CẤP ĐỘ 2: XỬ LÝ SONG SONG (MULTITHREAD) ===
                def compare_single_page(page_idx):
                    """So sánh một page đơn lẻ - được gọi trong thread pool"""
                    sheet_name = colored_sheets[page_idx] if page_idx < len(colored_sheets) else f"Page_{page_idx}"
                    
                    img_new = new_images[page_idx]
                    img_old = old_images[page_idx]
                    
                    # === CẤP ĐỘ 3: SỬ DỤNG OPENCV ===
                    if OPENCV_AVAILABLE and compare_images_opencv:
                        # Quick check - skip heavy processing if identical
                        if quick_compare_hash(img_new, img_old):
                            return (page_idx, sheet_name, None, False, "Không có sai khác")
                        
                        # Use OpenCV for fast comparison
                        left_img, right_img = compare_images_opencv(
                            img_new, img_old,
                            diff_threshold=threshold,
                            dilate_size=dilate_size,
                            dilate_iterations=dilate_iterations,
                            highlight_color=highlight_color,
                            fill_opacity=fill_opacity
                        )
                        side_by_side = create_side_by_side(left_img, right_img)
                        has_diff = True  # OpenCV always creates overlay, check bbox later
                        
                    else:
                        # Fallback: PIL-based comparison
                        from PIL import ImageChops, ImageFilter, Image
                        
                        if img_new.size != img_old.size:
                            img_old = img_old.resize(img_new.size, Image.Resampling.LANCZOS)
                        
                        diff = ImageChops.difference(img_new.convert('RGB'), img_old.convert('RGB'))
                        diff_gray = diff.convert('L')
                        mask = diff_gray.point(lambda x: 255 if x > threshold else 0)
                        
                        eff_dilate_size = dilate_size if dilate_size % 2 == 1 else max(1, dilate_size - 1)
                        for _ in range(dilate_iterations):
                            mask = mask.filter(ImageFilter.MaxFilter(eff_dilate_size))
                        
                        has_diff = mask.getbbox() is not None
                        
                        if has_diff:
                            hex_color = highlight_color.lstrip('#')
                            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                            alpha = int(255 * fill_opacity / 100)
                            
                            red_overlay = Image.new('RGBA', img_new.size, (r, g, b, alpha))
                            overlay_masked = Image.new('RGBA', img_new.size, (0, 0, 0, 0))
                            overlay_masked.paste(red_overlay, (0, 0), mask.convert('L'))
                            
                            combined_new = Image.alpha_composite(img_new.convert('RGBA'), overlay_masked)
                            left_img = img_old.convert('RGB')
                            right_img = combined_new.convert('RGB')
                            
                            side_width = left_img.width + right_img.width
                            side_height = max(left_img.height, right_img.height)
                            
                            side_by_side = Image.new('RGB', (side_width, side_height), (255, 255, 255))
                            side_by_side.paste(left_img, (0, 0))
                            side_by_side.paste(right_img, (left_img.width, 0))
                        else:
                            side_by_side = None
                    
                    if has_diff and side_by_side:
                        safe_sheet_name = sheet_name.replace('|', '_').replace(' ', '_').replace('/', '_')
                        comparison_img_path = os.path.join(output_folder, f"comparison_{idx}_{safe_sheet_name}.png")
                        side_by_side.save(comparison_img_path, "PNG")
                        
                        comparison_pdf_path = os.path.join(output_folder, f"comparison_{idx}_{safe_sheet_name}.pdf")
                        side_by_side.save(comparison_pdf_path, "PDF", resolution=float(dpi))
                        
                        return (page_idx, sheet_name, comparison_img_path, True, "Có sai khác", comparison_pdf_path)
                    else:
                        return (page_idx, sheet_name, None, False, "Không có sai khác", None)
                
                # === CHẠY SONG SONG VỚI THREADPOOLEXECUTOR ===
                max_workers = min(4, num_pages)  # Giới hạn 4 thread để tránh quá tải
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(compare_single_page, p): p for p in range(num_pages)}
                    
                    for future in as_completed(futures):
                        result = future.result()
                        page_idx, sheet_name, comparison_img_path, has_diff, message = result[:5]
                        comparison_pdf_path = result[5] if len(result) > 5 else None
                        
                        if has_diff and comparison_img_path:
                            file_comparison_images[sheet_name] = comparison_img_path
                            if comparison_pdf_path:
                                file_comparison_pdfs.append(comparison_pdf_path)
                                all_comparison_pdfs.append(comparison_pdf_path)
                            self.report_service.add_result(file_name, sheet_name, "FAIL", message, comparison_img_path)
                        else:
                            self.report_service.add_result(file_name, sheet_name, "OK", message)
                
                # Step 5: Create per-file Excel result (LEGACY FORMAT)
                if file_comparison_images:
                    if status_callback:
                        status_callback(f"Creating Excel result for {file_name}")
                    
                    ReportService.create_per_file_excel_result(
                        new_file_path=new_path,
                        comparison_images=file_comparison_images,
                        old_images=None,
                        output_folder=output_folder,
                        is_pdf_method=True,
                        dpi=dpi
                    )

                    
                    # Cleanup comparison images sau khi đã chèn vào Excel
                    for img_path in file_comparison_images.values():
                        try:
                            if img_path and os.path.exists(img_path):
                                os.remove(img_path)
                        except:
                            pass
                
                # Giữ PDF mới và rename thành {filename}.pdf (legacy behavior)
                # Chỉ xóa PDF cũ
                try:
                    # Rename CTTTmoi PDF -> {original_filename}.pdf
                    original_filename = os.path.splitext(os.path.basename(new_path))[0]
                    final_pdf_path = os.path.join(output_folder, f"{original_filename}.pdf")
                    
                    if os.path.exists(pdf_new_path):
                        if os.path.exists(final_pdf_path):
                            os.remove(final_pdf_path)
                        os.rename(pdf_new_path, final_pdf_path)
                        utils.logger.info(f"Renamed PDF: {pdf_new_path} -> {final_pdf_path}")
                    
                    # Xóa PDF cũ (không cần giữ)
                    if os.path.exists(pdf_old_path):
                        os.remove(pdf_old_path)
                except Exception as e:
                    utils.logger.warning(f"Error during PDF cleanup/rename: {e}")
                    
            except Exception as e:
                utils.logger.error(f"Error processing {file_name}: {e}")
                self.report_service.add_result(file_name, "N/A", "ERROR", str(e))
        
        # Cleanup all comparison PDFs - không cần nữa vì đã có Excel result
        for pdf_path in all_comparison_pdfs:
            try:
                if pdf_path and os.path.exists(pdf_path):
                    os.remove(pdf_path)
            except:
                pass
        
        return all_comparison_pdfs

    def _process_screenshot_workflow(self, new_files, old_files, output_folder, status_callback=None):
        """
        STRATEGY B: Screenshot Comparison Workflow
        
        Logic:
        1. Mở từng cặp file Excel (new/old)
        2. Tìm các sheet có màu tab xanh
        3. Cut/Paste vùng EX:GR vào file tạm
        4. Chụp ảnh màn hình từng sheet
        5. So sánh ảnh và highlight khác biệt
        
        Đây là phương pháp "Cut/Paste + Screenshot" từ legacy code.
        """
        from PIL import Image, ImageChops, ImageDraw, ImageFilter
        from services.screenshot_service import ScreenshotService
        
        screenshot_service = ScreenshotService()
        comparison_results = []
        
        # Settings
        settings = self.settings or {}
        threshold = settings.get('pdf_diff_threshold', config.DEFAULT_DIFF_THRESHOLD)
        fill_opacity = settings.get('highlight_fill_opacity', config.DEFAULT_FILL_OPACITY)
        fill_color = settings.get('highlight_fill_color', config.HIGHLIGHT_FILL_COLOR)
        dilate_size = settings.get('pdf_dilate_size', config.DEFAULT_DILATE_SIZE)
        dilate_iterations = settings.get('pdf_dilate_iterations', config.DEFAULT_DILATE_ITERATIONS)
        
        total_files = len(new_files)
        
        for idx, (new_path, old_path) in enumerate(zip(new_files, old_files), 1):
            file_name = os.path.basename(new_path)
            file_comparison_images = {}  # {sheet_name: comparison_img_path}
            
            if status_callback:
                status_callback(f"Screenshot: Đang xử lý cặp {idx}/{total_files}: {file_name}")
            
            try:
                # Mở file mới để tìm sheet có màu xanh
                wb_new = self.excel_service.open_workbook(new_path, read_only=True)
                if not wb_new:
                    self.report_service.add_result(file_name, "N/A", "ERROR", "Không thể mở file mới")
                    continue
                
                # Lấy danh sách sheet có màu xanh
                colored_sheets = []
                for sheet in wb_new.Sheets:
                    if sheet.Tab.Color == config.COLOR_GREEN_TAB:
                        colored_sheets.append(sheet.Name.rstrip())
                
                self.excel_service.close_workbook(wb_new)
                
                if not colored_sheets:
                    self.report_service.add_result(file_name, "N/A", "ERROR", "Không tìm thấy sheet màu xanh")
                    continue
                
                utils.logger.info(f"Found {len(colored_sheets)} green sheets in {file_name}: {colored_sheets}")
                
                # Chụp ảnh từ file mới
                if status_callback:
                    status_callback(f"Screenshot: Chụp ảnh file mới...")
                
                new_screenshots = self._capture_sheets_to_images(
                    new_path, colored_sheets, output_folder, "CTTTmoi", status_callback
                )
                
                if not new_screenshots:
                    self.report_service.add_result(file_name, "N/A", "ERROR", "Không chụp được ảnh file mới")
                    continue
                
                # Chụp ảnh từ file cũ
                if status_callback:
                    status_callback(f"Screenshot: Chụp ảnh file cũ...")
                
                old_screenshots = self._capture_sheets_to_images(
                    old_path, colored_sheets, output_folder, "CTTTcu", status_callback
                )
                
                if not old_screenshots:
                    self.report_service.add_result(file_name, "N/A", "ERROR", "Không chụp được ảnh file cũ")
                    continue
                
                # So sánh từng cặp ảnh
                if status_callback:
                    status_callback(f"Screenshot: So sánh ảnh...")
                
                for sheet_name in colored_sheets:
                    new_img_path = new_screenshots.get(sheet_name)
                    old_img_path = old_screenshots.get(sheet_name)
                    
                    if not new_img_path or not old_img_path:
                        self.report_service.add_result(file_name, sheet_name, "ERROR", "Thiếu ảnh")
                        continue
                    
                    if not os.path.exists(new_img_path) or not os.path.exists(old_img_path):
                        self.report_service.add_result(file_name, sheet_name, "ERROR", "File ảnh không tồn tại")
                        continue
                    
                    # So sánh ảnh
                    try:
                        img_new = Image.open(new_img_path)
                        img_old = Image.open(old_img_path)
                        
                        # Resize nếu kích thước khác nhau
                        if img_new.size != img_old.size:
                            img_old = img_old.resize(img_new.size, Image.Resampling.LANCZOS)
                        
                        diff = ImageChops.difference(img_new.convert('RGB'), img_old.convert('RGB'))
                        diff_gray = diff.convert('L')
                        
                        # Tạo mask
                        mask = diff_gray.point(lambda x: 255 if x > threshold else 0)
                        
                        # Dilate
                        eff_dilate = dilate_size if dilate_size % 2 == 1 else max(1, dilate_size - 1)
                        for _ in range(dilate_iterations):
                            mask = mask.filter(ImageFilter.MaxFilter(eff_dilate))
                        
                        if mask.getbbox():
                            # Có sự khác biệt
                            hex_color = fill_color.lstrip('#')
                            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                            alpha = int(255 * fill_opacity / 100)
                            
                            overlay = Image.new('RGBA', img_new.size, (r, g, b, alpha))
                            overlay_masked = Image.new('RGBA', img_new.size, (0, 0, 0, 0))
                            overlay_masked.paste(overlay, (0, 0), mask.convert('L'))
                            
                            combined = Image.alpha_composite(img_new.convert('RGBA'), overlay_masked)
                            
                            # Tạo ảnh side-by-side
                            left = img_old.convert('RGB')
                            right = combined.convert('RGB')
                            
                            side = Image.new('RGB', (left.width + right.width, max(left.height, right.height)), (255, 255, 255))
                            side.paste(left, (0, 0))
                            side.paste(right, (left.width, 0))
                            
                            # Lưu kết quả
                            safe_name = sheet_name.replace('|', '_').replace(' ', '_').replace('/', '_')
                            result_path = os.path.join(output_folder, f"{file_name}_{safe_name}_so_sanh.png")
                            side.save(result_path, "PNG")
                            
                            comparison_results.append(result_path)
                            file_comparison_images[sheet_name] = result_path  # For per-file Excel result
                            self.report_service.add_result(file_name, sheet_name, "FAIL", "Có sai khác", result_path)
                        else:
                            # Không có sự khác biệt
                            self.report_service.add_result(file_name, sheet_name, "OK", "Không có sai khác")
                        
                    except Exception as e:
                        utils.logger.error(f"Error comparing images for {sheet_name}: {e}")
                        self.report_service.add_result(file_name, sheet_name, "ERROR", str(e))
                
                # Cleanup temp screenshots
                for path in list(new_screenshots.values()) + list(old_screenshots.values()):
                    try:
                        if path and os.path.exists(path):
                            os.remove(path)
                    except:
                        pass
                
                # Create per-file Excel result (LEGACY FORMAT)
                if file_comparison_images:
                    if status_callback:
                        status_callback(f"Creating Excel result for {file_name}")
                    
                    from services.report_service import ReportService
                    ReportService.create_per_file_excel_result(
                        new_file_path=new_path,
                        comparison_images=file_comparison_images,
                        old_images=old_screenshots,  # Pass old screenshots for side by side
                        output_folder=output_folder,
                        is_pdf_method=False,
                        dpi=100
                    )
                    
                    # Cleanup comparison images sau khi đã chèn vào Excel
                    for img_path in file_comparison_images.values():
                        try:
                            if img_path and os.path.exists(img_path):
                                os.remove(img_path)
                        except:
                            pass
            except Exception as e:
                utils.logger.error(f"Screenshot workflow error for {file_name}: {e}")
                self.report_service.add_result(file_name, "N/A", "ERROR", str(e))
        
        return comparison_results

    def _capture_sheets_to_images(self, file_path, sheet_names, output_folder, prefix, status_callback=None):
        """
        Chụp ảnh các sheet từ file Excel theo logic legacy:
        1. Mở file gốc
        2. Tạo workbook tạm
        3. Copy vùng EX:ZZ từ mỗi sheet sang workbook tạm
        4. Chụp ảnh từ workbook tạm (để có layout chuẩn)
        
        Returns:
            Dict {sheet_name: image_path}
        """
        import pythoncom
        import win32com.client
        import time
        import tempfile
        
        screenshots = {}
        excel = None
        source_workbook = None
        temp_workbook = None
        temp_path = None
        temp_dir = None
        
        try:
            pythoncom.CoInitialize()
            
            # Tạo Excel instance
            excel = win32com.client.Dispatch("Excel.Application")
            excel.DisplayAlerts = False
            excel.EnableEvents = False
            
            # Mở file source (ẩn)
            excel.Visible = False
            file_path = os.path.abspath(file_path)
            utils.unblock_file(file_path)
            
            source_workbook = excel.Workbooks.Open(
                file_path, 
                UpdateLinks=False, 
                ReadOnly=True, 
                Notify=False
            )
            
            # Tạo temp workbook
            temp_workbook = excel.Workbooks.Add()
            temp_dir = tempfile.mkdtemp(dir=output_folder)
            temp_path = os.path.join(temp_dir, f"__temp_{prefix}_{int(time.time())}.xlsx")
            temp_workbook.SaveAs(temp_path)
            
            # Xóa sheet mặc định trừ 1
            while temp_workbook.Sheets.Count > 1:
                temp_workbook.Sheets(temp_workbook.Sheets.Count).Delete()
            
            # Xử lý từng sheet
            zoom_level = self.settings.get('zoom', 46) if self.settings else 46
            
            for idx, sheet_name in enumerate(sheet_names):
                try:
                    # Tìm sheet trong source
                    source_sheet = None
                    try:
                        source_sheet = source_workbook.Sheets(sheet_name)
                    except:
                        # Thử với variant 1 (dash → underscore)
                        try:
                            variant1 = sheet_name.replace("-", "_")
                            source_sheet = source_workbook.Sheets(variant1)
                            utils.logger.info(f"Found sheet with variant name: '{variant1}' for '{sheet_name}'")
                        except:
                            # Thử với variant 2 (underscore → dash)
                            try:
                                variant2 = sheet_name.replace("_", "-")
                                source_sheet = source_workbook.Sheets(variant2)
                                utils.logger.info(f"Found sheet with variant name: '{variant2}' for '{sheet_name}'")
                            except:
                                utils.logger.warning(f"Sheet '{sheet_name}' not found in source file")
                                continue
                    
                    if not source_sheet:
                        continue
                    
                    # Tạo hoặc lấy sheet trong temp workbook
                    if idx == 0:
                        temp_sheet = temp_workbook.Sheets(1)
                        temp_sheet.Name = f"Temp_{sheet_name[:25]}" if len(sheet_name) > 25 else f"Temp_{sheet_name}"
                    else:
                        temp_sheet = temp_workbook.Sheets.Add(After=temp_workbook.Sheets(temp_workbook.Sheets.Count))
                        temp_sheet.Name = f"Temp_{sheet_name[:25]}" if len(sheet_name) > 25 else f"Temp_{sheet_name}"
                    
                    # Copy vùng EX:ZZ từ source sang temp (A1)
                    try:
                        source_range = source_sheet.Range("EX:ZZ")
                        source_range.Copy(Destination=temp_sheet.Range("A1"))
                        utils.logger.info(f"Copied EX:ZZ from '{sheet_name}' to temp sheet")
                    except Exception as copy_err:
                        # Fallback: Copy bằng clipboard
                        try:
                            source_range = source_sheet.Range("EX:ZZ")
                            source_range.Copy()
                            time.sleep(0.3)
                            temp_sheet.Paste(Destination=temp_sheet.Range("A1"))
                            utils.logger.info(f"Copy-pasted EX:ZZ from '{sheet_name}' via clipboard")
                        except Exception as paste_err:
                            utils.logger.error(f"Failed to copy data for {sheet_name}: {paste_err}")
                            continue
                    
                    # Cập nhật row height như legacy
                    try:
                        temp_sheet.Rows(1).RowHeight = 20
                        temp_sheet.Range("2:76").RowHeight = 12
                    except:
                        pass
                    
                    # Activate temp sheet và chuẩn bị chụp
                    temp_sheet.Activate()
                    
                    # Set zoom
                    try:
                        excel.ActiveWindow.Zoom = zoom_level
                    except:
                        pass
                    
                    # Tắt gridlines
                    try:
                        excel.ActiveWindow.DisplayGridlines = False
                    except:
                        pass
                    
                    # Navigate to A1
                    try:
                        temp_sheet.Range("A1").Select()
                        excel.ActiveWindow.ScrollRow = 1
                        excel.ActiveWindow.ScrollColumn = 1
                    except:
                        pass
                    
                    # Bây giờ mới show Excel và bring to foreground
                    excel.Visible = True
                    excel.ScreenUpdating = True
                    
                    try:
                        excel.WindowState = -4137  # xlMaximized
                    except:
                        pass
                    
                    try:
                        import win32gui
                        import win32con
                        hwnd = excel.Hwnd
                        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                        win32gui.SetForegroundWindow(hwnd)
                    except:
                        pass
                    
                    # Ẩn Ribbon
                    try:
                        excel.ExecuteExcel4Macro("SHOW.TOOLBAR(\"Ribbon\",False)")
                    except:
                        pass
                    
                    # Đợi Excel ổn định
                    time.sleep(1.5)
                    
                    # Chụp ảnh
                    from services.screenshot_service import ScreenshotService
                    safe_name = sheet_name.replace('|', '_').replace(' ', '_').replace('/', '_')
                    img_path = os.path.join(output_folder, f"{prefix}_{safe_name}.png")
                    
                    if ScreenshotService.capture_excel_sheet(excel, temp_sheet, img_path):
                        screenshots[sheet_name] = img_path
                        utils.logger.info(f"Screenshot saved: {img_path}")
                    else:
                        utils.logger.warning(f"Failed to capture screenshot for {sheet_name}")
                    
                    # Ẩn Excel lại sau mỗi sheet để giảm nhấp nháy
                    excel.Visible = False
                    
                except Exception as e:
                    utils.logger.error(f"Error processing sheet {sheet_name}: {e}")
                    
        except Exception as e:
            utils.logger.error(f"Error in _capture_sheets_to_images: {e}")
        finally:
            # Cleanup
            try:
                if temp_workbook:
                    temp_workbook.Close(SaveChanges=False)
            except:
                pass
            try:
                if source_workbook:
                    source_workbook.Close(SaveChanges=False)
            except:
                pass
            try:
                if excel:
                    excel.Quit()
            except:
                pass
            # Xóa file temp
            try:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                if temp_dir and os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
            pythoncom.CoUninitialize()
        
        return screenshots


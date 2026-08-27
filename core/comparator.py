import os
import sys
import shutil
import tempfile
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
        goto_addr = settings.get('goto_address')
        if not goto_addr or str(goto_addr).strip().upper() in ['A1', '']:
            goto_addr = config.DEFAULT_GOTO_ADDRESS
        legacy_service.set_goto_address(goto_addr)
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

        settings = settings or {}
        self.settings = settings

        # Validate the selected document type before creating an output folder.
        # This prevents a wrong mode from silently completing with an empty result.
        from services.validation_service import ValidationService
        selected_mode = settings.get("doc_mode", config.DOC_MODE_STANDARD_CTTT)
        is_valid_mode, mode_error = ValidationService.validate_document_mode(
            new_file_list, old_file_list, selected_mode
        )
        if not is_valid_mode:
            raise ValueError(mode_error)

              # Start timing
        start_time = time.time()
        
        # Determine Output Folder
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        preferred_folder = settings.get("output_folder", None)
        
        if preferred_folder and os.path.exists(preferred_folder):
            target_output_folder = os.path.join(preferred_folder, f"{config.DEFAULT_OUTPUT_FOLDER_NAME}_{timestamp}")
        else:
            target_output_folder = utils.get_writable_dir(os.path.dirname(new_file_list[0]), f"{config.DEFAULT_OUTPUT_FOLDER_NAME}_{timestamp}")
        
        target_output_folder = os.path.normpath(target_output_folder)
        os.makedirs(target_output_folder, exist_ok=True)
        utils.logger.info(f"Results will be saved to: {target_output_folder}")
        
        # Check if working with network paths (UNC share or remote drive)
        is_network = (
            any(utils.is_network_path(p) for p in new_file_list + old_file_list) or
            utils.is_network_path(target_output_folder)
        )
        
        local_temp_workspace = None
        working_new_files = list(new_file_list)
        working_old_files = list(old_file_list)
        working_output_folder = target_output_folder
        
        if is_network:
            import tempfile
            local_temp_workspace = os.path.join(tempfile.gettempdir(), f"CTTT_FastCache_{os.getpid()}_{int(time.time())}")
            os.makedirs(local_temp_workspace, exist_ok=True)
            utils.logger.info(f"[Fast-Cache] Network drive detected. Created local SSD workspace: {local_temp_workspace}")
            
            # Fast copy input files to local SSD
            if status_callback:
                status_callback("Đang nạp file vào bộ nhớ đệm SSD...")
                
            local_in_new = os.path.join(local_temp_workspace, "Input_New")
            local_in_old = os.path.join(local_temp_workspace, "Input_Old")
            os.makedirs(local_in_new, exist_ok=True)
            os.makedirs(local_in_old, exist_ok=True)
            
            working_new_files = []
            for f in new_file_list:
                local_f = os.path.join(local_in_new, os.path.basename(f))
                shutil.copy2(f, local_f)
                working_new_files.append(local_f)
                
            working_old_files = []
            for f in old_file_list:
                local_f = os.path.join(local_in_old, os.path.basename(f))
                shutil.copy2(f, local_f)
                working_old_files.append(local_f)
                
            working_output_folder = os.path.join(local_temp_workspace, "Output")
            os.makedirs(working_output_folder, exist_ok=True)

        suppress = settings.get("suppress_error", True) if settings else True
        self.excel_service = ExcelService(suppress_alerts=suppress)

        # Determine Document Mode & Print Area
        doc_mode = settings.get("doc_mode", config.DOC_MODE_STANDARD_CTTT) if settings else config.DOC_MODE_STANDARD_CTTT
        if doc_mode == config.DOC_MODE_DUKC_CTTT:
            default_print_area = config.PRINT_AREA_DUKC_CTTT
        elif doc_mode == config.DOC_MODE_DUKC_OTHER:
            default_print_area = config.PRINT_AREA_DUKC_OTHER
        else:
            default_print_area = config.PRINT_AREA_STANDARD_CTTT
            
        print_area = settings.get("print_area") if settings and settings.get("print_area") else default_print_area
        utils.logger.info(f"Comparison Mode: {doc_mode}, Print Area: {print_area}")

        try:
            # --- Preprocessing Phase ---
            processed_new_files = []
            processed_old_files = []
            
            if doc_mode == config.DOC_MODE_STANDARD_CTTT:
                if status_callback: status_callback("Preprocessing files...")
                
                # Preprocess New Files
                new_sheet_names_collection = {} # Map file_idx -> list of (old, new) sheet names
                do_auto_b = settings.get("auto_add_b", False) if settings else False
                
                for idx, f_path in enumerate(working_new_files):
                     proc_path, sheet_mapping = self.excel_service.standard_preprocess(f_path, is_new=True, auto_add_b=do_auto_b)
                     processed_new_files.append(proc_path)
                     new_sheet_names_collection[idx] = sheet_mapping
                     
                # Preprocess Old Files (with 'b' logic)
                for idx, f_path in enumerate(working_old_files):
                    ref_mapping = new_sheet_names_collection.get(idx, [])
                    proc_path, _ = self.excel_service.standard_preprocess(f_path, is_new=False, auto_add_b=do_auto_b, new_sheet_names_ref=ref_mapping) 
                    processed_old_files.append(proc_path)
            else:
                # DUKC modes: Keep original format intact
                processed_new_files = list(working_new_files)
                processed_old_files = list(working_old_files)

            # Init Report
            from services.report_service import ReportService
            self.report_service = ReportService(working_output_folder)
            
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
                    working_output_folder, 
                    status_callback
                )
                
                # Cleanup temp files
                if status_callback:
                    status_callback("Dọn dẹp file tạm...")
                CleanupService.cleanup_temp_images(working_output_folder, keep_diff_images=True)
                CleanupService.cleanup_per_sheet_pdfs(working_output_folder)
                
            else:
                # STRATEGY B: Screenshot Comparison Workflow
                utils.logger.info("Using Screenshot comparison workflow")
                if status_callback:
                    status_callback("Đang sử dụng phương pháp Screenshot (Cut/Paste)...")
                
                self._process_screenshot_workflow(
                    processed_new_files, 
                    processed_old_files, 
                    working_output_folder, 
                    status_callback
                )
                
                # Cleanup temp files
                if status_callback:
                    status_callback("Dọn dẹp file tạm...")
                CleanupService.cleanup_temp_images(working_output_folder, keep_diff_images=True)
            
            # Sync back to network output if Fast-Cache was active
            if is_network and local_temp_workspace:
                if status_callback:
                    status_callback("Đang đồng bộ kết quả lên ổ mạng...")
                utils.logger.info(f"[Fast-Cache] Syncing results from {working_output_folder} to {target_output_folder}")
                utils.sync_folder_to_destination(working_output_folder, target_output_folder)

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            minutes, seconds = divmod(elapsed_time, 60)
            
            # Per-file results đã được tạo trong workflow
            utils.logger.info(f"Comparison completed in {int(minutes)} phút {seconds:.2f} giây")
            if status_callback: 
                status_callback(f"Hoàn tất! Thời gian: {int(minutes)} phút {seconds:.2f} giây")
            os.startfile(target_output_folder)
            
            return elapsed_time
                
        except Exception as e:
            utils.logger.error(f"Comparison Error: {e}")
            raise
        finally:
            if self.excel_service:
                self.excel_service.cleanup()
            if local_temp_workspace and os.path.exists(local_temp_workspace):
                try:
                    shutil.rmtree(local_temp_workspace, ignore_errors=True)
                except Exception:
                    pass

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
        
        doc_mode = self.settings.get('doc_mode', config.DOC_MODE_STANDARD_CTTT) if self.settings else config.DOC_MODE_STANDARD_CTTT
        if doc_mode == config.DOC_MODE_DUKC_CTTT:
            default_print_area = config.PRINT_AREA_DUKC_CTTT
        elif doc_mode == config.DOC_MODE_DUKC_OTHER:
            default_print_area = config.PRINT_AREA_DUKC_OTHER
        else:
            default_print_area = config.PRINT_AREA_STANDARD_CTTT
        print_area = self.settings.get('print_area') if self.settings and self.settings.get('print_area') else default_print_area
        
        total_files = len(new_file_list)
        all_comparison_pdfs = []  # For final merged PDF
        self.last_compared_count = 0
        
        for idx, (new_path, old_path) in enumerate(zip(new_file_list, old_file_list)):
            file_started_at = time.perf_counter()
            file_name = os.path.basename(new_path)
            file_comparison_images = {}  # {sheet_name: comparison_img_path}
            file_comparison_pdfs = []
            
            if status_callback:
                status_callback(f"Processing {idx+1}/{total_files}: {file_name}")
            
            try:
                if doc_mode == config.DOC_MODE_STANDARD_CTTT:
                    # STANDARD CTTT: Green sheets detection
                    if status_callback:
                        status_callback(f"Exporting PDF (NEW): {file_name}")
                        
                    pdf_new_path = os.path.join(output_folder, f"CTTTmoi_{idx}.pdf")
                    success_new, colored_sheets = self.pdf_service.export_green_sheets_direct(new_path, pdf_new_path, print_area=print_area, _keep_alive=True)
                    
                    if not success_new or not colored_sheets:
                        # Fallback
                        colored_sheets = self.pdf_service.get_colored_sheets(new_path)
                        if not colored_sheets:
                            utils.logger.warning(f"No green-tab sheets found in {file_name}")
                            self.report_service.add_result(file_name, "N/A", "WARNING", "Không tìm thấy sheet màu xanh")
                            continue
                        success_new = self.pdf_service.export_sheets_to_pdf_with_retry(new_path, colored_sheets, pdf_new_path, print_area=print_area)
                        if not success_new:
                            self.report_service.add_result(file_name, "N/A", "ERROR", "Không xuất được PDF mới")
                            continue
                    
                    # Step 3: Export OLD file sheets to PDF
                    if status_callback:
                        status_callback(f"Exporting PDF (OLD): {os.path.basename(old_path)}")
                        
                    pdf_old_path = os.path.join(output_folder, f"CTTTcu_{idx}.pdf")
                    success_old = self.pdf_service.export_sheets_to_pdf_with_retry(old_path, colored_sheets, pdf_old_path, print_area=print_area, _keep_alive=True)
                    
                    if not success_old:
                        self.report_service.add_result(file_name, "N/A", "ERROR", "Không xuất được PDF cũ")
                        continue
                    sheets_to_compare = colored_sheets
                    
                elif doc_mode == config.DOC_MODE_DUKC_OTHER:
                    # DUKC OTHER MODE: CHỈ SO SÁNH SHEET FORM (không phân biệt hoa thường)
                    if status_callback:
                        status_callback(f"Finding sheet 'Form': {file_name}")
                    form_sheet_new = self.pdf_service.find_sheet_by_name(new_path, "form")
                    form_sheet_old = self.pdf_service.find_sheet_by_name(old_path, "form")

                    if not form_sheet_new:
                        utils.logger.warning(f"Sheet 'Form' not found in NEW file {file_name}")
                        self.report_service.add_result(file_name, "Form", "MISSING", "Không tìm thấy sheet 'Form' ở file mới")
                        continue

                    if not form_sheet_old:
                        utils.logger.warning(f"Sheet 'Form' not found in OLD file {os.path.basename(old_path)}")
                        self.report_service.add_result(file_name, "Form", "MISSING", "Không tìm thấy sheet 'Form' ở file cũ")
                        continue

                    if status_callback:
                        status_callback(f"Exporting PDF (NEW - {form_sheet_new}): {file_name}")
                    pdf_new_path = os.path.join(output_folder, f"CTTTmoi_{idx}.pdf")
                    success_new = self.pdf_service.export_sheets_to_pdf_with_retry(new_path, [form_sheet_new], pdf_new_path, print_area=print_area, _keep_alive=True)
                    if not success_new:
                        self.report_service.add_result(file_name, form_sheet_new, "ERROR", "Không xuất được PDF mới")
                        continue

                    if status_callback:
                        status_callback(f"Exporting PDF (OLD - {form_sheet_old}): {os.path.basename(old_path)}")
                    pdf_old_path = os.path.join(output_folder, f"CTTTcu_{idx}.pdf")
                    # Normalize the OLD sheet geometry to NEW in memory. Fractional
                    # row/column size drift otherwise makes unchanged text reflow and
                    # produces widespread pixel-level false positives in PDF output.
                    success_old = self.pdf_service.export_sheets_to_pdf_with_retry(
                        old_path, [form_sheet_old], pdf_old_path,
                        print_area=print_area, _keep_alive=True,
                        layout_reference_path=new_path
                    )
                    if not success_old:
                        self.report_service.add_result(file_name, form_sheet_old, "ERROR", "Không xuất được PDF cũ")
                        continue
                    sheets_to_compare = getattr(self.pdf_service, 'last_exported_page_labels', None) or [form_sheet_new]

                else:
                    # DUKC CTTT MODE: Visible sheets with exact sheet name matching
                    if status_callback:
                        status_callback(f"Reading visible sheets: {file_name}")
                    # XLSX/XLSM metadata avoids two expensive Excel COM opens.
                    visible_new = self.pdf_service.get_visible_sheets_fast(new_path)
                    visible_old = self.pdf_service.get_visible_sheets_fast(old_path)
                    if visible_new is None:
                        visible_new = self.pdf_service.get_visible_sheets(new_path)
                    if visible_old is None:
                        visible_old = self.pdf_service.get_visible_sheets(old_path)
                    
                    matching_sheets = []
                    for s in visible_new:
                        if s in visible_old:
                            matching_sheets.append(s)
                        else:
                            utils.logger.warning(f"Sheet '{s}' in NEW file not found in OLD file {os.path.basename(old_path)}")
                            self.report_service.add_result(file_name, s, "MISSING", "Không tìm thấy sheet tương ứng ở file cũ")
                            
                    for s in visible_old:
                        if s not in visible_new:
                            utils.logger.warning(f"Sheet '{s}' in OLD file not found in NEW file {file_name}")
                            self.report_service.add_result(file_name, s, "MISSING", "Sheet có trong file cũ nhưng không có trong file mới")
                            
                    if not matching_sheets:
                        utils.logger.warning(f"No matching visible sheets found between {file_name} and {os.path.basename(old_path)}")
                        self.report_service.add_result(file_name, "N/A", "WARNING", "Không tìm thấy sheet nào khớp tên giữa 2 file")
                        continue

                    if status_callback:
                        status_callback(f"Exporting PDF (NEW): {file_name}")
                    pdf_new_path = os.path.join(output_folder, f"CTTTmoi_{idx}.pdf")
                    success_new = self.pdf_service.export_sheets_to_pdf_with_retry(
                        new_path, matching_sheets, pdf_new_path,
                        print_area=print_area, _keep_alive=True
                    )
                    if not success_new:
                        self.report_service.add_result(file_name, "N/A", "ERROR", "Không xuất được PDF mới")
                        continue
                        
                    if status_callback:
                        status_callback(f"Exporting PDF (OLD): {os.path.basename(old_path)}")
                    pdf_old_path = os.path.join(output_folder, f"CTTTcu_{idx}.pdf")
                    success_old = self.pdf_service.export_sheets_to_pdf_with_retry(old_path, matching_sheets, pdf_old_path, print_area=print_area, _keep_alive=True)
                    if not success_old:
                        self.report_service.add_result(file_name, "N/A", "ERROR", "Không xuất được PDF cũ")
                        continue
                    sheets_to_compare = getattr(self.pdf_service, 'last_exported_page_labels', None) or matching_sheets

                utils.logger.info(
                    f"[Timing] PDF export {file_name}: {time.perf_counter() - file_started_at:.2f}s"
                )
                
                # Step 4: Compare PDFs page by page
                if status_callback:
                    status_callback(f"Comparing: {file_name}")
                
                new_images = self.pdf_service.render_pdf_to_images(pdf_new_path, dpi)
                old_images = self.pdf_service.render_pdf_to_images(pdf_old_path, dpi)
                
                num_pages = min(len(new_images), len(old_images))
                
                # === CẤP ĐỘ 2: XỬ LÝ SONG SONG (MULTITHREAD) ===
                def compare_single_page(page_idx):
                    """So sánh một page đơn lẻ - được gọi trong thread pool"""
                    sheet_name = sheets_to_compare[page_idx] if page_idx < len(sheets_to_compare) else f"Page_{page_idx}"
                    
                    img_new = new_images[page_idx]
                    img_old = old_images[page_idx]
                    
                    # === CẤP ĐỘ 3: SỬ DỤNG OPENCV ===
                    if OPENCV_AVAILABLE and compare_images_opencv:
                        # Quick check - skip heavy processing if identical
                        if quick_compare_hash(img_new, img_old):
                            return (page_idx, sheet_name, None, False, "Không có sai khác", None)
                        
                        # Use OpenCV for fast comparison
                        left_img, right_img, has_diff, diff_count = compare_images_opencv(
                            img_new, img_old,
                            diff_threshold=threshold,
                            dilate_size=dilate_size,
                            dilate_iterations=dilate_iterations,
                            highlight_color=highlight_color,
                            fill_opacity=fill_opacity
                        )
                        side_by_side = create_side_by_side(left_img, right_img) if has_diff else None
                    else:
                        # Fallback: PIL-based comparison
                        left_img, right_img, has_diff, diff_count = compare_images_pil(
                            img_new, img_old,
                            diff_threshold=threshold,
                            dilate_size=dilate_size,
                            dilate_iterations=dilate_iterations,
                            highlight_color=highlight_color,
                            fill_opacity=fill_opacity
                        )
                        side_by_side = create_side_by_side(left_img, right_img) if has_diff else None
                    
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
                max_workers = min(4, num_pages) if num_pages > 0 else 1
                results_by_page = [None] * num_pages
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(compare_single_page, p): p for p in range(num_pages)}
                    
                    for future in as_completed(futures):
                        result = future.result()
                        p_idx = result[0]
                        results_by_page[p_idx] = result
                
                # === GOM KẾT QUẢ THEO ĐÚNG THỨ TỰ TUẦN TỰ TRANG (P1 -> P2 -> P3) ===
                for result in results_by_page:
                    if result is None:
                        continue
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

                utils.logger.info(
                    f"[Timing] Total compare {file_name}: {time.perf_counter() - file_started_at:.2f}s"
                )

                self.last_compared_count += 1
                
                # === FIX 3: Free rendered images from RAM before next file ===
                del new_images
                del old_images
                
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
                        
                    # Xóa các file so sánh PDF tạm của file này
                    for pdf_path in file_comparison_pdfs:
                        try:
                            if pdf_path and os.path.exists(pdf_path):
                                os.remove(pdf_path)
                        except Exception:
                            pass
                except Exception as e:
                    utils.logger.warning(f"Error during PDF cleanup/rename: {e}")
                    
            except Exception as e:
                utils.logger.error(f"Error processing {file_name}: {e}")
                self.report_service.add_result(file_name, "N/A", "ERROR", str(e))
        
        # Cleanup all comparison PDFs - toàn bộ ảnh so sánh đã nằm trọn vẹn trong file Excel kết quả
        for pdf_path in all_comparison_pdfs:
            try:
                if pdf_path and os.path.exists(pdf_path):
                    os.remove(pdf_path)
            except Exception:
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
                
                doc_mode = settings.get('doc_mode', config.DOC_MODE_STANDARD_CTTT)
                colored_sheets = []

                if doc_mode == config.DOC_MODE_DUKC_OTHER:
                    for sheet in wb_new.Sheets:
                        try:
                            if sheet.Name.strip().lower() == "form":
                                colored_sheets.append(sheet.Name.rstrip())
                                break
                        except Exception:
                            continue
                elif doc_mode == config.DOC_MODE_DUKC_CTTT:
                    for sheet in wb_new.Sheets:
                        try:
                            is_visible = (sheet.Visible == -1 or sheet.Visible is True or sheet.Visible == 1)
                            if is_visible:
                                colored_sheets.append(sheet.Name.rstrip())
                        except Exception:
                            continue
                else:
                    for sheet in wb_new.Sheets:
                        try:
                            if int(sheet.Tab.Color) == config.COLOR_GREEN_TAB:
                                colored_sheets.append(sheet.Name.rstrip())
                        except Exception:
                            continue
                
                self.excel_service.close_workbook(wb_new)
                
                if not colored_sheets:
                    err_msg = "Không tìm thấy sheet 'Form'" if doc_mode == config.DOC_MODE_DUKC_OTHER else "Không tìm thấy sheet màu xanh"
                    self.report_service.add_result(file_name, "N/A", "ERROR", err_msg)
                    continue
                
                utils.logger.info(f"Found {len(colored_sheets)} sheets to compare in {file_name}: {colored_sheets}")
                
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
                        side = None
                        has_diff = False
                        
                        # === FIX 2: Short-circuit for identical images ===
                        if OPENCV_AVAILABLE and quick_compare_hash:
                            if quick_compare_hash(img_new, img_old):
                                self.report_service.add_result(file_name, sheet_name, "OK", "Không có sai khác")
                                continue
                        
                        # === SỬ DỤNG OPENCV HOẶC PIL ===
                        if OPENCV_AVAILABLE and compare_images_opencv:
                            left_img, right_img, has_diff, diff_count = compare_images_opencv(
                                img_new, img_old,
                                diff_threshold=threshold,
                                dilate_size=dilate_size,
                                dilate_iterations=dilate_iterations,
                                highlight_color=fill_color,
                                fill_opacity=fill_opacity
                            )
                            side = create_side_by_side(left_img, right_img) if has_diff else None
                        else:
                            # Fallback: PIL-based comparison
                            left_img, right_img, has_diff, diff_count = compare_images_pil(
                                img_new, img_old,
                                diff_threshold=threshold,
                                dilate_size=dilate_size,
                                dilate_iterations=dilate_iterations,
                                highlight_color=fill_color,
                                fill_opacity=fill_opacity
                            )
                            side = create_side_by_side(left_img, right_img) if has_diff else None
                        
                        if has_diff and side is not None:
                            safe_name = sheet_name.replace('|', '_').replace(' ', '_').replace('/', '_')
                            result_path = os.path.join(output_folder, f"{file_name}_{safe_name}_so_sanh.png")
                            side.save(result_path, "PNG")
                            comparison_results.append(result_path)
                            file_comparison_images[sheet_name] = result_path
                            self.report_service.add_result(file_name, sheet_name, "FAIL", "Có sai khác", result_path)
                        else:
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
            try:
                excel = win32com.client.Dispatch("Excel.Application")
            except Exception:
                excel = win32com.client.DispatchEx("Excel.Application")
            try:
                excel.DisplayAlerts = False
            except Exception:
                pass
            try:
                excel.EnableEvents = False
            except Exception:
                pass
            try:
                excel.Visible = False
            except Exception:
                pass
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
            zoom_level = self.settings.get('zoom', config.DEFAULT_ZOOM) if self.settings else config.DEFAULT_ZOOM
            
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
                    try:
                        excel.Visible = True
                    except Exception:
                        pass
                    try:
                        excel.ScreenUpdating = True
                    except Exception:
                        pass
                    
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
                    try:
                        excel.Visible = False
                    except Exception:
                        pass
                    
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


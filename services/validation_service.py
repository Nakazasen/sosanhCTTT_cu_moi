"""
Validation Service - Kiểm tra và xác thực dữ liệu đầu vào

Bao gồm:
- Validation cho các giá trị cấu hình (DPI, threshold, etc.)
- Input sanitization
- File validation
- Message box helpers với suppression support
"""

import os
import tkinter as tk
from tkinter import messagebox
import config
import utils


class ValidationService:
    """Service validation và message handling."""
    
    # Default ranges
    DPI_MIN = 50
    DPI_MAX = 300
    DPI_DEFAULT = 100
    
    THRESHOLD_MIN = 0
    THRESHOLD_MAX = 255
    THRESHOLD_DEFAULT = 40
    
    DILATE_SIZE_MIN = 1
    DILATE_SIZE_MAX = 9
    DILATE_SIZE_DEFAULT = 3
    
    DILATE_ITER_MIN = 1
    DILATE_ITER_MAX = 3
    DILATE_ITER_DEFAULT = 2
    
    OPACITY_MIN = 0
    OPACITY_MAX = 100
    OPACITY_DEFAULT = 40
    
    # =========================================================================
    # VALUE VALIDATION
    # =========================================================================
    
    @staticmethod
    def validate_dpi(value, auto_fix=True):
        """
        Validate DPI value.
        
        Args:
            value: Giá trị DPI cần validate
            auto_fix: Nếu True, tự động điều chỉnh về giá trị hợp lệ
            
        Returns:
            Tuple (is_valid, fixed_value, error_message)
        """
        try:
            dpi = int(value)
            
            if dpi < ValidationService.DPI_MIN:
                if auto_fix:
                    return (False, ValidationService.DPI_MIN, 
                           f"DPI tối thiểu là {ValidationService.DPI_MIN}. Đã điều chỉnh.")
                return (False, dpi, f"DPI phải >= {ValidationService.DPI_MIN}")
            
            if dpi > ValidationService.DPI_MAX:
                if auto_fix:
                    return (False, ValidationService.DPI_MAX,
                           f"DPI tối đa là {ValidationService.DPI_MAX}. Đã điều chỉnh.")
                return (False, dpi, f"DPI phải <= {ValidationService.DPI_MAX}")
            
            return (True, dpi, None)
            
        except (ValueError, TypeError):
            if auto_fix:
                return (False, ValidationService.DPI_DEFAULT,
                       f"DPI không hợp lệ. Đã reset về {ValidationService.DPI_DEFAULT}.")
            return (False, None, "DPI phải là số nguyên")
    
    @staticmethod
    def validate_threshold(value, auto_fix=True):
        """Validate difference threshold (0-255)."""
        try:
            val = int(value)
            
            if val < ValidationService.THRESHOLD_MIN:
                if auto_fix:
                    return (False, ValidationService.THRESHOLD_MIN, "Ngưỡng tối thiểu là 0")
                return (False, val, "Ngưỡng phải >= 0")
            
            if val > ValidationService.THRESHOLD_MAX:
                if auto_fix:
                    return (False, ValidationService.THRESHOLD_MAX, "Ngưỡng tối đa là 255")
                return (False, val, "Ngưỡng phải <= 255")
            
            return (True, val, None)
            
        except (ValueError, TypeError):
            if auto_fix:
                return (False, ValidationService.THRESHOLD_DEFAULT, "Ngưỡng không hợp lệ")
            return (False, None, "Ngưỡng phải là số nguyên")
    
    @staticmethod
    def validate_dilate_size(value, auto_fix=True):
        """Validate dilate size (1-9, odd number)."""
        try:
            val = int(value)
            
            if val < ValidationService.DILATE_SIZE_MIN:
                if auto_fix:
                    return (False, ValidationService.DILATE_SIZE_MIN, "Độ dày tối thiểu là 1")
                return (False, val, "Độ dày phải >= 1")
            
            if val > ValidationService.DILATE_SIZE_MAX:
                if auto_fix:
                    return (False, ValidationService.DILATE_SIZE_MAX, "Độ dày tối đa là 9")
                return (False, val, "Độ dày phải <= 9")
            
            # Ensure odd number
            if val % 2 == 0:
                fixed = max(1, val - 1)
                if auto_fix:
                    return (False, fixed, "Độ dày phải là số lẻ. Đã điều chỉnh.")
                return (False, val, "Độ dày phải là số lẻ")
            
            return (True, val, None)
            
        except (ValueError, TypeError):
            if auto_fix:
                return (False, ValidationService.DILATE_SIZE_DEFAULT, "Độ dày không hợp lệ")
            return (False, None, "Độ dày phải là số nguyên lẻ")
    
    @staticmethod
    def validate_dilate_iterations(value, auto_fix=True):
        """Validate dilate iterations (1-3)."""
        try:
            val = int(value)
            
            val = max(ValidationService.DILATE_ITER_MIN, 
                     min(ValidationService.DILATE_ITER_MAX, val))
            
            return (True, val, None)
            
        except (ValueError, TypeError):
            if auto_fix:
                return (False, ValidationService.DILATE_ITER_DEFAULT, "Số lần nở không hợp lệ")
            return (False, None, "Số lần nở phải là số nguyên 1-3")
    
    @staticmethod
    def validate_opacity(value, auto_fix=True):
        """Validate opacity percentage (0-100)."""
        try:
            val = int(value)
            
            val = max(ValidationService.OPACITY_MIN, 
                     min(ValidationService.OPACITY_MAX, val))
            
            return (True, val, None)
            
        except (ValueError, TypeError):
            if auto_fix:
                return (False, ValidationService.OPACITY_DEFAULT, "Độ mờ không hợp lệ")
            return (False, None, "Độ mờ phải là số 0-100")
    
    @staticmethod
    def validate_hex_color(value, auto_fix=True):
        """Validate hex color code."""
        if not value:
            if auto_fix:
                return (False, "#ff0000", "Màu không được để trống")
            return (False, None, "Màu không được để trống")
        
        color = value.strip()
        
        # Add # if missing
        if not color.startswith('#'):
            color = '#' + color
        
        # Check format
        if len(color) != 7:
            if auto_fix:
                return (False, "#ff0000", "Mã màu không hợp lệ")
            return (False, None, "Mã màu phải có định dạng #RRGGBB")
        
        try:
            int(color[1:], 16)
            return (True, color, None)
        except ValueError:
            if auto_fix:
                return (False, "#ff0000", "Mã màu không hợp lệ")
            return (False, None, "Mã màu chứa ký tự không hợp lệ")
    
    # =========================================================================
    # FILE VALIDATION
    # =========================================================================
    
    @staticmethod
    def validate_excel_file(file_path):
        """
        Validate Excel file.
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not file_path:
            return (False, "Đường dẫn file trống")
        
        if not os.path.exists(file_path):
            return (False, f"File không tồn tại: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ('.xlsx', '.xls', '.xlsm'):
            return (False, f"File không phải Excel: {ext}")
        
        # Check if file is readable
        try:
            with open(file_path, 'rb') as f:
                _ = f.read(1)
            return (True, None)
        except PermissionError:
            return (False, f"Không có quyền đọc file: {file_path}")
        except Exception as e:
            return (False, f"Lỗi đọc file: {e}")
    
    @staticmethod
    def validate_file_pairs(new_files, old_files):
        """
        Validate file pairs for comparison.
        
        Returns:
            Tuple (is_valid, error_message)
        """
        if not new_files:
            return (False, "Chưa chọn file CTTT mới")
        
        if not old_files:
            return (False, "Chưa chọn file CTTT cũ")
        
        if len(new_files) != len(old_files):
            return (False, f"Số file không khớp: {len(new_files)} mới vs {len(old_files)} cũ")
        
        # Validate each file
        for i, (new_f, old_f) in enumerate(zip(new_files, old_files)):
            valid, err = ValidationService.validate_excel_file(new_f)
            if not valid:
                return (False, f"Cặp {i+1} - File mới lỗi: {err}")
            
            valid, err = ValidationService.validate_excel_file(old_f)
            if not valid:
                return (False, f"Cặp {i+1} - File cũ lỗi: {err}")
        
        return (True, None)

    @staticmethod
    def _inspect_workbook(file_path):
        """Read the sheet metadata needed to validate a selected document mode."""
        import posixpath
        import zipfile
        from xml.etree import ElementTree

        extension = os.path.splitext(file_path)[1].lower()
        if extension not in ('.xlsx', '.xlsm'):
            return None

        spreadsheet_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        relationship_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        package_relationship_ns = "http://schemas.openxmlformats.org/package/2006/relationships"

        with zipfile.ZipFile(file_path) as archive:
            workbook_xml = ElementTree.fromstring(archive.read("xl/workbook.xml"))
            relationships_xml = ElementTree.fromstring(
                archive.read("xl/_rels/workbook.xml.rels")
            )
            relationship_targets = {
                item.attrib["Id"]: item.attrib["Target"]
                for item in relationships_xml.findall(
                    f"{{{package_relationship_ns}}}Relationship"
                )
            }

            sheets = []
            for sheet in workbook_xml.findall(
                f".//{{{spreadsheet_ns}}}sheet"
            ):
                relation_id = sheet.attrib.get(f"{{{relationship_ns}}}id")
                target = relationship_targets.get(relation_id, "")
                if target.startswith("/"):
                    worksheet_path = target.lstrip("/")
                else:
                    worksheet_path = posixpath.normpath(posixpath.join("xl", target))

                rgb = None
                has_content = False
                if worksheet_path in archive.namelist():
                    worksheet_xml = ElementTree.fromstring(archive.read(worksheet_path))
                    tab_color = worksheet_xml.find(
                        f"./{{{spreadsheet_ns}}}sheetPr/{{{spreadsheet_ns}}}tabColor"
                    )
                    if tab_color is not None and tab_color.attrib.get("rgb"):
                        rgb = tab_color.attrib["rgb"][-6:].upper()
                    # Keep the fast-path behaviour aligned with Excel's UsedRange
                    # check: do not compare a merely visible, empty worksheet.
                    has_content = worksheet_xml.find(
                        f".//{{{spreadsheet_ns}}}sheetData/{{{spreadsheet_ns}}}row/{{{spreadsheet_ns}}}c"
                    ) is not None

                sheets.append({
                    "name": sheet.attrib.get("name", ""),
                    "visible": sheet.attrib.get("state", "visible") == "visible",
                    "tab_rgb": rgb,
                    "has_content": has_content,
                })
            return sheets

    @staticmethod
    def validate_document_mode(new_files, old_files, doc_mode):
        """Ensure selected workbooks structurally match the requested comparison mode."""
        valid_pairs, pair_error = ValidationService.validate_file_pairs(new_files, old_files)
        if not valid_pairs:
            return False, pair_error

        # Excel stores COLOR_GREEN_TAB as BGR while openpyxl exposes RGB.
        ole_color = config.COLOR_GREEN_TAB
        expected_green = f"{ole_color & 0xFF:02X}{(ole_color >> 8) & 0xFF:02X}{(ole_color >> 16) & 0xFF:02X}"
        errors = []

        for pair_index, (new_path, old_path) in enumerate(zip(new_files, old_files), 1):
            try:
                new_sheets = ValidationService._inspect_workbook(new_path)
                old_sheets = ValidationService._inspect_workbook(old_path)
            except Exception as error:
                errors.append(
                    f"Cặp {pair_index}: không thể đọc cấu trúc workbook ({error})."
                )
                continue

            # Legacy .xls cannot be inspected safely without launching Excel; let the
            # existing COM workflow validate those files later.
            if new_sheets is None or old_sheets is None:
                continue

            new_names = {item["name"].strip().lower() for item in new_sheets}
            old_names = {item["name"].strip().lower() for item in old_sheets}
            new_label = os.path.basename(new_path)
            old_label = os.path.basename(old_path)

            if doc_mode == config.DOC_MODE_DUKC_OTHER:
                missing = []
                if "form" not in new_names:
                    missing.append(f"file mới '{new_label}'")
                if "form" not in old_names:
                    missing.append(f"file cũ '{old_label}'")
                if missing:
                    errors.append(
                        f"Cặp {pair_index}: chế độ 'Tờ Phát Hành DUKC & Khác' yêu cầu "
                        f"sheet 'Form', nhưng không tìm thấy trong {', '.join(missing)}."
                    )

            elif doc_mode == config.DOC_MODE_STANDARD_CTTT:
                new_green = {
                    item["name"].strip().lower()
                    for item in new_sheets if item["tab_rgb"] == expected_green
                }
                old_green = {
                    item["name"].strip().lower()
                    for item in old_sheets if item["tab_rgb"] == expected_green
                }
                if "form" in new_names and "form" in old_names:
                    errors.append(
                        f"Cặp {pair_index}: cả hai file có sheet 'Form', không phù hợp với "
                        "'CTTT thông thường'. Hãy chọn 'Tờ Phát Hành DUKC & Khác'."
                    )
                elif not new_green:
                    suggestion = (
                        " File có sheet 'Form'; hãy chọn loại 'Tờ Phát Hành DUKC & Khác'."
                        if "form" in new_names else ""
                    )
                    errors.append(
                        f"Cặp {pair_index}: file mới '{new_label}' không có sheet tab xanh "
                        f"dành cho CTTT tiêu chuẩn.{suggestion}"
                    )
                elif not (new_green & old_green):
                    errors.append(
                        f"Cặp {pair_index}: không có sheet tab xanh trùng tên giữa "
                        f"'{new_label}' và '{old_label}'."
                    )

            elif doc_mode == config.DOC_MODE_DUKC_CTTT:
                visible_new = {
                    item["name"].strip().lower() for item in new_sheets if item["visible"]
                }
                visible_old = {
                    item["name"].strip().lower() for item in old_sheets if item["visible"]
                }
                if "form" in new_names and "form" in old_names:
                    errors.append(
                        f"Cặp {pair_index}: cả hai file có sheet 'Form'. Có thể bạn đã chọn "
                        "nhầm loại; hãy dùng 'Tờ Phát Hành DUKC & Khác'."
                    )
                elif not (visible_new & visible_old):
                    errors.append(
                        f"Cặp {pair_index}: không có sheet hiển thị trùng tên giữa "
                        f"'{new_label}' và '{old_label}'."
                    )

        if errors:
            return False, "Loại tài liệu đã chọn không phù hợp:\n\n" + "\n".join(errors)
        return True, None
    
    @staticmethod
    def validate_output_folder(folder_path):
        """Validate output folder."""
        if not folder_path:
            return (True, None)  # Empty is OK, will use default
        
        if os.path.exists(folder_path):
            if not os.path.isdir(folder_path):
                return (False, "Đường dẫn không phải thư mục")
            
            # Check write permission
            try:
                test_file = os.path.join(folder_path, ".test_write")
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write("test")
                os.remove(test_file)
                return (True, None)
            except Exception:
                return (False, "Không có quyền ghi vào thư mục này")
        else:
            # Try to create
            try:
                os.makedirs(folder_path, exist_ok=True)
                return (True, None)
            except Exception:
                return (False, "Không thể tạo thư mục")


class MessageHandler:
    """Handler cho message boxes với suppression support."""
    
    def __init__(self, suppress=False, status_callback=None):
        """
        Args:
            suppress: Nếu True, không hiển thị popup, chỉ log
            status_callback: Function(text) để cập nhật status
        """
        self.suppress = suppress
        self.status_callback = status_callback
    
    def error(self, title, message):
        """Show error message."""
        if self.suppress:
            utils.logger.error(f"[SUPPRESSED] {title}: {message}")
            if self.status_callback:
                self.status_callback(f"❌ {message}")
        else:
            messagebox.showerror(title, message)
    
    def warning(self, title, message):
        """Show warning message."""
        if self.suppress:
            utils.logger.warning(f"[SUPPRESSED] {title}: {message}")
            if self.status_callback:
                self.status_callback(f"⚠️ {message}")
        else:
            messagebox.showwarning(title, message)
    
    def info(self, title, message):
        """Show info message."""
        if self.suppress:
            utils.logger.info(f"[SUPPRESSED] {title}: {message}")
            if self.status_callback:
                self.status_callback(message)
        else:
            messagebox.showinfo(title, message)
    
    def ask_yes_no(self, title, message):
        """Ask yes/no question."""
        if self.suppress:
            utils.logger.info(f"[SUPPRESSED ASK] {title}: {message} -> Auto: Yes")
            return True  # Auto-answer Yes when suppressed
        else:
            return messagebox.askyesno(title, message)
    
    def ask_ok_cancel(self, title, message):
        """Ask OK/Cancel question."""
        if self.suppress:
            utils.logger.info(f"[SUPPRESSED ASK] {title}: {message} -> Auto: OK")
            return True
        else:
            return messagebox.askokcancel(title, message)

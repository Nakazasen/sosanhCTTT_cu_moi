import os
import time
import win32com.client
import pythoncom
import config
import utils

class ExcelService:
    def __init__(self, suppress_alerts=True):
        self.app = None
        self.pid = None
        self.suppress_alerts = suppress_alerts
        self._initialize_excel()

    def _initialize_excel(self):
        """Initializes Excel Application safely with retry and fallback logic."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                pythoncom.CoInitialize()
                self.app = win32com.client.Dispatch("Excel.Application")
                
                # Set properties with individual error handling
                try:
                    self.app.Visible = False
                except Exception as e:
                    utils.logger.warning(f"Could not set Visible=False: {e}")
                    # Try alternative approach - create new instance
                    try:
                        self.app = win32com.client.DispatchEx("Excel.Application")
                        self.app.Visible = False
                    except Exception:
                        pass
                
                try:
                    self.app.DisplayAlerts = not self.suppress_alerts
                except Exception:
                    pass
                
                try:
                    self.app.EnableEvents = False
                except Exception:
                    pass
                
                try:
                    self.app.ScreenUpdating = False
                except Exception:
                    pass
                
                self.pid = utils.get_excel_pid(self.app)
                utils.logger.info(f"Excel Instance Started (PID: {self.pid})")
                return  # Success
                
            except Exception as e:
                utils.logger.warning(f"Excel init attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    # Try to clean up any existing Excel process
                    try:
                        if self.app:
                            self.app.Quit()
                    except:
                        pass
                    pythoncom.CoUninitialize()
                else:
                    utils.logger.error(f"Failed to initialize Excel after {max_retries} attempts: {e}")
                    raise

    def open_workbook(self, file_path, read_only=True):
        """Opens a workbook safely."""
        try:
            # Ensure absolute path (Excel requirement)
            file_path = os.path.abspath(file_path)
            
            # Attempt to unblock file (Remove MotW) to prevent Protected View
            utils.unblock_file(file_path)
            
            wb = self.app.Workbooks.Open(
                file_path, 
                UpdateLinks=False, 
                ReadOnly=read_only, 
                Notify=False, 
                AddToMru=False
            )
            return wb
        except Exception as e:
            utils.logger.error(f"Failed to open workbook {file_path}: {e}")
            return None

    def close_workbook(self, wb, save_changes=False):
        """Closes a workbook."""
        try:
            if wb:
                wb.Close(SaveChanges=save_changes)
        except Exception:
            pass

    def create_new_workbook(self):
        """Creates a new workbook."""
        return self.app.Workbooks.Add()

    def cleanup(self):
        """Quits Excel and ensures process cleanup."""
        try:
            if self.app:
                self.app.Quit()
        except Exception:
            pass
        
        # Force kill if needed
        if self.pid:
            utils.kill_specific_excel_process(self.pid)
        pythoncom.CoUninitialize()

    def copy_range_direct(self, source_sheet, target_sheet, source_range_addr="EX:ZZ", target_cell_addr="A1"):
        """
        Copies range directly without Clipboard using Range.Copy destination.
        Preserves formats, images, shapes, and column widths.
        """
        try:
            source_range = source_sheet.Range(source_range_addr)
            target_cell = target_sheet.Range(target_cell_addr)
            
            # Direct Copy (Internal Excel copy)
            source_range.Copy(Destination=target_cell)
            
            return True
        except Exception as e:
            utils.logger.error(f"Direct copy failed: {e}")
            # Fallback could go here if needed, but Direct Copy is robust
            return False

    def format_sheet_layout(self, sheet):
        """Applies specific row heights as per requirements."""
        try:
            sheet.Rows(1).RowHeight = 20
            sheet.Range("2:76").RowHeight = 12
        except Exception as e:
            utils.logger.warning(f"Failed to format sheet layout: {e}")

    def export_as_pdf(self, workbook, output_path, retries=3):
        """
        Exports workbook to PDF with retry logic and permission handling.
        """
        import time
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        # Check permissions/availability of output path
        final_output_path = output_path
        if os.path.exists(final_output_path):
            try:
                # Try to open/rename to check if locked
                temp_name = final_output_path + ".tmp"
                os.rename(final_output_path, temp_name)
                os.rename(temp_name, final_output_path)
            except OSError:
                # File is locked, try a different name
                base, ext = os.path.splitext(final_output_path)
                final_output_path = f"{base}_{int(time.time())}{ext}"
                utils.logger.warning(f"Output PDF locked. Switching to: {final_output_path}")

        for attempt in range(retries):
            try:
                workbook.ExportAsFixedFormat(0, final_output_path) # 0 = xlTypePDF
                
                if os.path.exists(final_output_path) and os.path.getsize(final_output_path) > 0:
                    try:
                        from services.pdf_service import PDFService
                        PDFService.normalize_pdf_to_a4(final_output_path)
                    except Exception:
                        pass
                    return final_output_path
            except Exception as e:
                utils.logger.warning(f"Export PDF attempt {attempt+1} failed: {e}")
                time.sleep(1)
        
        # Fallback: Try exporting active sheet only if whole workbook fails? 
        # Or standard internal error -> return None
        return None

    def _make_unique_sheet_name(self, workbook, new_name, max_length=31):
        """
        Tạo tên sheet duy nhất và đảm bảo không quá 31 ký tự.
        
        Args:
            workbook: COM workbook object
            new_name: Tên sheet mới mong muốn
            max_length: Độ dài tối đa của tên sheet (Excel limit = 31)
            
        Returns:
            Tên sheet duy nhất
        """
        # Truncate if too long
        if len(new_name) > max_length:
            new_name = new_name[:max_length]
        
        existing = [s.Name for s in workbook.Sheets]
        if new_name not in existing:
            return new_name
        
        # Add suffix until unique
        counter = 1
        while True:
            suffix = f"_{counter}"
            # Ensure total length doesn't exceed limit
            truncated = new_name[:max_length - len(suffix)] + suffix
            if truncated not in existing:
                return truncated
            counter += 1
            if counter > 100:  # Safety limit
                break
        
        return new_name  # Fallback to original

    def standard_preprocess(self, file_path, is_new=True, auto_add_b=False, new_sheet_names_ref=None):
        """
        Performs standard preprocessing matching Legacy v7.03 behavior:
        - Rename file (replace underscores)
        - Rename sheets (replace special characters _, ., ,, |)
        - Change font to Times New Roman for EX:ZZ
        - Add 'b' prefix if auto_add_b is enabled
        
        Args:
            file_path (str): Path to the Excel file.
            is_new (bool): True for new files (processes green-tab sheets), False for old files (processes all sheets).
            auto_add_b (bool): Whether to auto-add 'b' prefix for barcode comparison.
            new_sheet_names_ref (list): List of (original, final) or final sheet names from the corresponding new file.
        
        Returns:
            tuple: (final_file_path, sheet_name_mapping)
        """
        # 1. Safe Rename File
        final_file_path = utils.safe_rename_file(file_path)
        final_file_path = os.path.abspath(final_file_path)
        utils.unblock_file(final_file_path)
        
        # 2. Open Workbook
        wb = self.open_workbook(final_file_path, read_only=False)
        if not wb:
            return final_file_path, []
            
        sheet_name_mapping = []
        try:
            modified = False
            
            # Determine sheets to process
            if is_new:
                # File mới: Chỉ xử lý sheet có màu tab xanh (5296274)
                sheets_to_process = []
                for sheet in wb.Sheets:
                    try:
                        if sheet.Tab.Color == config.COLOR_GREEN_TAB:
                            sheets_to_process.append(sheet)
                    except Exception:
                        continue
            else:
                # File cũ: Duyệt tất cả các sheet trong workbook
                sheets_to_process = list(wb.Sheets)
            
            for sheet in sheets_to_process:
                try:
                    original_name = sheet.Name
                    new_name = original_name.rstrip()
                    
                    # Normalize Chars (_, ., ,, | -> - hoặc khoảng trắng)
                    new_name = new_name.replace("_", "-").replace(".", "-").replace(",", "-").replace("|", " ")
                    
                    if is_new:
                        # File mới: thêm 'b' nếu bật auto_add_b và chưa có 'b'
                        if auto_add_b and not new_name.lower().startswith('b'):
                            new_name = 'b' + new_name
                    else:
                        # File cũ: thêm 'b' nếu sheet tương ứng trong file mới có 'b'
                        if auto_add_b and new_sheet_names_ref:
                            for ref in new_sheet_names_ref:
                                # ref có thể là tuple (orig, final) hoặc chuỗi final_name
                                final_new_name = ref[1] if isinstance(ref, (list, tuple)) else str(ref)
                                if final_new_name.lower().startswith('b'):
                                    target_check = final_new_name[1:]
                                    if (new_name == target_check or 
                                        new_name.replace("_", "-").replace(".", "-").replace(",", "-").replace("|", " ") == target_check):
                                        if not new_name.lower().startswith('b'):
                                            new_name = 'b' + new_name
                                        break
                    
                    # Rename if changed
                    if new_name != original_name:
                        try:
                            unique_name = self._make_unique_sheet_name(wb, new_name)
                            sheet.Name = unique_name
                            modified = True
                            sheet_name_mapping.append((original_name, unique_name))
                            utils.logger.info(f"Renamed sheet: '{original_name}' → '{unique_name}'")
                        except Exception as e:
                            utils.logger.warning(f"Could not rename sheet '{original_name}' to '{new_name}': {e}")
                            sheet_name_mapping.append((original_name, original_name))
                    else:
                        sheet_name_mapping.append((original_name, original_name))
                    
                    # Change Font for EX1:ZZ80 (Targeted CTTT range for fast execution)
                    try:
                        sheet.Range("EX1:ZZ80").Font.Name = "Times New Roman"
                        modified = True
                    except Exception:
                        pass
                except Exception as sheet_err:
                    utils.logger.warning(f"Skipping problematic sheet during preprocess: {sheet_err}")
                    continue
            
            if modified:
                wb.Save()
                utils.logger.info(f"Preprocessed and saved: {os.path.basename(final_file_path)}")
                
        except Exception as e:
            utils.logger.error(f"Preprocessing failed for {file_path}: {e}")
        finally:
            self.close_workbook(wb)
            
        return final_file_path, sheet_name_mapping

    def preprocess_dukc_form_sheet(self, file_path, output_dir=None, is_new=True):
        """
        Preprocesses Excel workbook for DUKC sheet 'Form' comparison:
        1. Creates a working copy in output_dir (or tempdir) to keep original user file untouched.
        2. Normalizes rich-text fonts in xl/sharedStrings.xml:
           - Forces all <rFont val="..."/> to 'Times New Roman' (stripping Yu Gothic, MS Mincho, etc.
             introduced when users copy-paste Japanese content).
           - Strictly PRESERVES all font colors (<color rgb="..."/>) so that business-critical
             red markings (FFFF0000) are completely intact.
        3. Normalizes text runs in sharedStrings.xml:
           - Strips leading/trailing newlines/whitespace from request paragraphs (e.g. B65 leading \n).
        
        Args:
            file_path (str): Original file path.
            output_dir (str, optional): Target directory for preprocessed file.
            is_new (bool): True for new file, False for old file (separates subdirectories).
            
        Returns:
            str: Path to the preprocessed temporary file.
        """
        if not file_path or not os.path.exists(file_path):
            return file_path

        import shutil
        import tempfile
        import zipfile
        import xml.etree.ElementTree as ET

        base_name = os.path.basename(file_path)
        sub_folder = "new" if is_new else "old"

        if output_dir and os.path.exists(output_dir):
            target_dir = os.path.join(output_dir, "_dukc_prep", sub_folder)
        else:
            target_dir = os.path.join(tempfile.gettempdir(), "_dukc_prep", sub_folder)
        os.makedirs(target_dir, exist_ok=True)

        target_file_path = os.path.join(target_dir, base_name)
        shutil.copy2(file_path, target_file_path)
        utils.unblock_file(target_file_path)

        try:
            ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
            ET.register_namespace('', 'http://schemas.openxmlformats.org/spreadsheetml/2006/main')

            with zipfile.ZipFile(target_file_path, 'r') as zin:
                namelist = zin.namelist()
                if 'xl/sharedStrings.xml' not in namelist:
                    return target_file_path
                other_files = {name: zin.read(name) for name in namelist if name != 'xl/sharedStrings.xml'}
                sst_data = zin.read('xl/sharedStrings.xml')

            sst_xml = ET.fromstring(sst_data)
            modified = False

            for si in sst_xml.findall(f'{ns}si'):
                runs = si.findall(f'{ns}r')
                if not runs:
                    t_elem = si.find(f'{ns}t')
                    if t_elem is not None and t_elem.text:
                        orig = t_elem.text
                        stripped = orig.strip('\r\n')
                        if stripped != orig:
                            t_elem.text = stripped
                            modified = True
                    continue

                # 1. Normalize font to Times New Roman across all runs
                for run in runs:
                    rPr = run.find(f'{ns}rPr')
                    if rPr is not None:
                        rFont = rPr.find(f'{ns}rFont')
                        if rFont is not None and rFont.attrib.get('val') != 'Times New Roman':
                            rFont.attrib['val'] = 'Times New Roman'
                            modified = True

                # 2. Strip leading newlines from first run with text
                for run in runs:
                    t_elem = run.find(f'{ns}t')
                    if t_elem is not None and t_elem.text:
                        lstr = t_elem.text.lstrip('\r\n')
                        if lstr != t_elem.text:
                            t_elem.text = lstr
                            modified = True
                        if t_elem.text:
                            break

                # 3. Strip trailing newlines from last run with text
                for run in reversed(runs):
                    t_elem = run.find(f'{ns}t')
                    if t_elem is not None and t_elem.text:
                        rstr = t_elem.text.rstrip('\r\n')
                        if rstr != t_elem.text:
                            t_elem.text = rstr
                            modified = True
                        if t_elem.text:
                            break

            if modified:
                new_sst = ET.tostring(sst_xml, encoding='utf-8', xml_declaration=True)
                with zipfile.ZipFile(target_file_path, 'w', zipfile.ZIP_DEFLATED) as zout:
                    for name, data in other_files.items():
                        zout.writestr(name, data)
                    zout.writestr('xl/sharedStrings.xml', new_sst)
                utils.logger.info(f"[DUKC Preprocess] Successfully normalized fonts & line breaks in: {base_name}")

        except Exception as e:
            utils.logger.warning(f"[DUKC Preprocess] Could not normalize {base_name}: {e}. Using copied file.")

        return target_file_path

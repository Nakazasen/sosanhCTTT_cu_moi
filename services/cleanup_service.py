"""
Cleanup Service - Quản lý file tạm và dọn dẹp

Ported từ Legacy SosanhCTTT để đảm bảo không còn file/folder rác.
"""

import os
import shutil
import glob
import tempfile
import utils


class CleanupService:
    """
    Service quản lý cleanup cho:
    - Thư mục tạm (tmp*)
    - File Excel tạm (__tmp_temp_*.xlsx)
    - File PDF từng sheet (CTTTmoi_*.pdf, CTTTcu_*.pdf)
    - Thư mục kết quả cũ
    """
    
    @staticmethod
    def cleanup_temp_folders(base_path):
        """
        Xóa tất cả thư mục tạm còn sót lại trong base_path.
        
        Args:
            base_path: Đường dẫn thư mục gốc cần dọn
        """
        try:
            if not os.path.exists(base_path):
                return
            
            removed_dirs = 0
            removed_files = 0
            
            # Xóa các thư mục tạm (bắt đầu bằng tmp)
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                
                if os.path.isdir(item_path):
                    # Thư mục tmp do tempfile.mkdtemp tạo ra
                    if item.startswith('tmp') and len(item) > 3:
                        try:
                            shutil.rmtree(item_path)
                            removed_dirs += 1
                        except Exception:
                            pass
            
            # Xóa các file Excel tạm
            for item in os.listdir(base_path):
                if item.startswith('__tmp_temp_') and item.endswith('.xlsx'):
                    item_path = os.path.join(base_path, item)
                    try:
                        os.remove(item_path)
                        removed_files += 1
                    except Exception:
                        pass
            
            if removed_dirs or removed_files:
                utils.logger.info(f"Cleanup: Đã xóa {removed_dirs} thư mục tạm, {removed_files} file tạm")
                
        except Exception as e:
            utils.logger.debug(f"Cleanup error: {e}")
    
    @staticmethod
    def cleanup_per_sheet_pdfs(base_path):
        """
        Xóa các file PDF từng sheet còn sót lại sau khi đã gộp.
        Không xóa: *_ALL_SHEETS.pdf, comparison_*.pdf
        
        Args:
            base_path: Đường dẫn thư mục output
        """
        try:
            if not os.path.exists(base_path):
                return
            
            patterns = [
                "CTTTmoi_*.pdf",
                "CTTTcu_*.pdf",
                "__tmp_CTTTmoi_*.pdf",
                "__tmp_CTTTcu_*.pdf",
                "temp_sheet_*.pdf",
                "Batch_Combined.pdf",  # Legacy batch workflow file
            ]
            
            keep_suffixes = ["_ALL_SHEETS.pdf"]
            keep_prefixes = ["comparison_"]
            
            removed = 0
            
            for pattern in patterns:
                for filepath in glob.glob(os.path.join(base_path, pattern)):
                    filename = os.path.basename(filepath)
                    
                    # Kiểm tra có nên giữ lại không
                    should_keep = False
                    for suffix in keep_suffixes:
                        if filename.endswith(suffix):
                            should_keep = True
                            break
                    for prefix in keep_prefixes:
                        if filename.startswith(prefix):
                            should_keep = True
                            break
                    
                    if should_keep:
                        continue
                    
                    try:
                        os.remove(filepath)
                        removed += 1
                    except Exception:
                        # File có thể đang bị lock bởi PDF viewer
                        pass
            
            if removed:
                utils.logger.info(f"Cleanup: Đã xóa {removed} file PDF tạm")
                
        except Exception as e:
            utils.logger.debug(f"Cleanup per-sheet PDFs error: {e}")
    
    @staticmethod
    def cleanup_temp_images(base_path, keep_diff_images=True):
        """
        Xóa các file ảnh tạm trong quá trình xử lý.
        
        Args:
            base_path: Đường dẫn thư mục
            keep_diff_images: Nếu True, giữ lại các ảnh sai khác (Diff_*.png)
        """
        try:
            if not os.path.exists(base_path):
                return
            
            patterns = [
                "page_*.png",  # Ảnh render từ PDF
                "CTTTmoi_*.png",  # Ảnh screenshot file mới
                "CTTTcu_*.png",  # Ảnh screenshot file cũ
            ]
            
            keep_prefixes = []
            if keep_diff_images:
                keep_prefixes.extend(["Diff_", "comparison_"])
            
            removed = 0
            
            for pattern in patterns:
                for filepath in glob.glob(os.path.join(base_path, pattern)):
                    filename = os.path.basename(filepath)
                    
                    should_keep = False
                    for prefix in keep_prefixes:
                        if filename.startswith(prefix):
                            should_keep = True
                            break
                    
                    if should_keep:
                        continue
                    
                    try:
                        os.remove(filepath)
                        removed += 1
                    except Exception:
                        pass
            
            if removed:
                utils.logger.info(f"Cleanup: Đã xóa {removed} file ảnh tạm")
                
        except Exception as e:
            utils.logger.debug(f"Cleanup images error: {e}")
    
    @staticmethod
    def full_cleanup(base_path, keep_diff_images=True):
        """
        Thực hiện dọn dẹp toàn diện.
        
        Args:
            base_path: Đường dẫn thư mục cần dọn
            keep_diff_images: Giữ lại ảnh sai khác hay không
        """
        CleanupService.cleanup_temp_folders(base_path)
        CleanupService.cleanup_per_sheet_pdfs(base_path)
        CleanupService.cleanup_temp_images(base_path, keep_diff_images)
        utils.logger.info("Cleanup: Hoàn tất dọn dẹp")
    
    @staticmethod
    def cleanup_old_result_folders(parent_path, folder_prefix="KetQuaSoSanh_CTTT", keep_count=5):
        """
        Xóa các thư mục kết quả cũ, chỉ giữ lại một số folder gần nhất.
        
        Args:
            parent_path: Thư mục cha chứa các folder kết quả
            folder_prefix: Tiền tố của folder kết quả
            keep_count: Số folder gần nhất cần giữ lại
        """
        try:
            if not os.path.exists(parent_path):
                return
            
            # Tìm tất cả folder kết quả
            result_folders = []
            
            for item in os.listdir(parent_path):
                item_path = os.path.join(parent_path, item)
                if os.path.isdir(item_path) and item.startswith(folder_prefix):
                    # Lấy thời gian sửa đổi
                    mtime = os.path.getmtime(item_path)
                    result_folders.append((item_path, mtime))
            
            # Sắp xếp theo thời gian (mới nhất trước)
            result_folders.sort(key=lambda x: x[1], reverse=True)
            
            # Xóa các folder cũ
            removed = 0
            for folder_path, _ in result_folders[keep_count:]:
                try:
                    shutil.rmtree(folder_path)
                    removed += 1
                except Exception:
                    pass
            
            if removed:
                utils.logger.info(f"Cleanup: Đã xóa {removed} thư mục kết quả cũ, giữ lại {keep_count} mới nhất")
                
        except Exception as e:
            utils.logger.debug(f"Cleanup old folders error: {e}")
    
    @staticmethod
    def create_temp_directory(base_path):
        """
        Tạo thư mục tạm trong base_path.
        
        Args:
            base_path: Đường dẫn thư mục cha
            
        Returns:
            Đường dẫn thư mục tạm hoặc None nếu thất bại
        """
        try:
            os.makedirs(base_path, exist_ok=True)
            temp_dir = tempfile.mkdtemp(dir=base_path)
            return temp_dir
        except Exception as e:
            utils.logger.error(f"Không thể tạo thư mục tạm: {e}")
            return None
    
    @staticmethod
    def safe_remove_file(filepath, max_retries=3, retry_delay=0.5):
        """
        Xóa file với retry logic.
        
        Args:
            filepath: Đường dẫn file cần xóa
            max_retries: Số lần thử tối đa
            retry_delay: Thời gian chờ giữa các lần thử (giây)
            
        Returns:
            True nếu xóa thành công hoặc file không tồn tại
        """
        import time
        
        if not os.path.exists(filepath):
            return True
        
        for attempt in range(max_retries):
            try:
                os.remove(filepath)
                return True
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except Exception:
                return False
        
        return False
    
    @staticmethod
    def safe_remove_directory(dirpath, max_retries=3, retry_delay=0.5):
        """
        Xóa thư mục với retry logic.
        
        Args:
            dirpath: Đường dẫn thư mục cần xóa
            max_retries: Số lần thử tối đa
            retry_delay: Thời gian chờ giữa các lần thử (giây)
            
        Returns:
            True nếu xóa thành công hoặc thư mục không tồn tại
        """
        import time
        
        if not os.path.exists(dirpath):
            return True
        
        for attempt in range(max_retries):
            try:
                shutil.rmtree(dirpath)
                return True
            except PermissionError:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except Exception:
                return False
        
        return False

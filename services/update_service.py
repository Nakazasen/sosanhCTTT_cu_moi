"""
Auto Update Service - Tự động cập nhật phần mềm từ server
Triển khai ngang từ Phanmem_copySoft_USB
"""
import os
import sys
import glob
import re
import shutil
import subprocess
import logging

# Constants cho Update
UPDATE_FOLDER = r"\\fstvn01\Data\10_Production Engineering Department(製造技術部)\02.製造技術課\PE Dept\15. FORM（BIEU MAU）-形式\Form_VBA\Form_Phanmem_sosanhCTTT"
UPDATE_FILE_PATTERN = "SosanhCTTT_phienban*.exe"

logger = logging.getLogger(__name__)


def get_current_version():
    """Lấy version hiện tại - ưu tiên từ config (đã có logic detect từ tên file exe)"""
    try:
        import config
        return config.APP_VERSION
    except Exception as e:
        logger.warning(f"Không thể lấy version từ config: {e}")
        return "UNKNOWN"


def compare_versions(ver1, ver2):
    """So sánh 2 version string a.b.c..., return True nếu ver1 > ver2"""
    try:
        parts1 = [int(x) for x in ver1.split('.')]
        parts2 = [int(x) for x in ver2.split('.')]
        return parts1 > parts2
    except:
        return False


def check_for_update():
    """
    Kiểm tra phiên bản mới từ folder share.
    Returns: (has_update: bool, newest_version: str, newest_file_path: str)
    """
    try:
        logger.info(f"Đang kiểm tra update từ: {UPDATE_FOLDER}")
        
        if not os.path.exists(UPDATE_FOLDER):
            logger.warning("⚠️ Không truy cập được folder update server.")
            return False, None, None

        search_pattern = os.path.join(UPDATE_FOLDER, UPDATE_FILE_PATTERN)
        files = glob.glob(search_pattern)
        
        if not files:
            logger.info("Không tìm thấy file update trên server.")
            return False, None, None
        
        newest_ver = None
        newest_file = None
        
        for f_path in files:
            filename = os.path.basename(f_path)
            # Tìm version trong tên file: SosanhCTTT_phienban7.04.exe -> 7.04
            match = re.search(r'phienban(\d+(\.\d+)*)', filename, re.IGNORECASE)
            if match:
                ver = match.group(1)
                if newest_ver is None or compare_versions(ver, newest_ver):
                    newest_ver = ver
                    newest_file = f_path
        
        if newest_ver is None:
            logger.info("Không tìm thấy version trong tên file update.")
            return False, None, None
        
        current_version = get_current_version()
        
        if compare_versions(newest_ver, current_version):
            logger.info(f"🆕 Có phiên bản mới: {newest_ver} (hiện tại: {current_version})")
            return True, newest_ver, newest_file
        else:
            logger.info(f"✅ Phần mềm đang ở phiên bản mới nhất: {current_version}")
            return False, None, None
            
    except Exception as e:
        logger.error(f"Lỗi kiểm tra update: {e}")
        return False, None, None


def perform_update(new_file_path, callback_on_start=None):
    """
    Thực hiện cập nhật tự động.
    
    Args:
        new_file_path: Đường dẫn đến file exe mới trên server
        callback_on_start: Callback trước khi bắt đầu update (để đóng UI)
    
    Returns:
        True nếu bắt đầu update thành công, False nếu lỗi
    """
    try:
        current_exe = sys.executable
        
        # Nếu đang chạy file .py thì không self-update được
        if not getattr(sys, 'frozen', False):
            logger.warning("Chức năng cập nhật chỉ hoạt động trên file .exe đã đóng gói.")
            return False

        # Lấy tên file gốc của bản update (ví dụ: SosanhCTTT_phienban7.04.exe)
        new_filename = os.path.basename(new_file_path)
        
        # Đường dẫn đích mới cho file exe sau khi update (cùng thư mục với file đang chạy)
        target_exe = os.path.join(os.path.dirname(current_exe), new_filename)
        
        # Copy file mới về dưới dạng tạm
        temp_exe = os.path.join(os.path.dirname(current_exe), "Update_Temp.exe")
        logger.info(f"Đang copy file update từ: {new_file_path}")
        shutil.copy2(new_file_path, temp_exe)
        
        # Tạo file batch để xử lý việc đổi tên và xóa file cũ
        batch_file = os.path.join(os.path.dirname(current_exe), "do_update.bat")
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write('chcp 65001 >nul\n')  # UTF-8
            f.write('echo Dang cap nhat phan mem...\n')
            f.write('timeout /t 2 /nobreak >nul\n')  # Chờ 2 giây để app cũ đóng
            f.write(f'del "{current_exe}"\n')  # Xóa bản cũ
            f.write(f'move "{temp_exe}" "{target_exe}"\n')  # Đổi tên temp thành version mới
            f.write(f'start "" "{target_exe}"\n')  # Chạy version mới
            f.write('(goto) 2>nul & del "%~f0"\n')  # Xóa file bat
        
        logger.info("Đã tạo file batch update, đang khởi động...")
        
        # Gọi callback trước khi thoát (để đóng UI)
        if callback_on_start:
            callback_on_start()
        
        # Chạy file batch và tắt app
        subprocess.Popen(batch_file, shell=True)
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Lỗi update: {e}")
        return False


# Tiện ích để dùng với Tkinter
class TkinterUpdateHelper:
    """Helper class để tích hợp với Tkinter UI"""
    
    def __init__(self, master, on_update_available=None):
        """
        Args:
            master: Tkinter root window
            on_update_available: Callback khi có update, nhận (version, file_path)
        """
        self.master = master
        self.on_update_available = on_update_available
    
    def check_update_async(self, delay_ms=1000):
        """Kiểm tra update sau delay_ms mili giây"""
        self.master.after(delay_ms, self._do_check_update)
    
    def _do_check_update(self):
        """Thực hiện kiểm tra update"""
        has_update, newest_ver, newest_file = check_for_update()
        
        if has_update and self.on_update_available:
            self.on_update_available(newest_ver, newest_file)
    
    def show_update_dialog(self, newest_ver, newest_file):
        """Hiển thị dialog hỏi người dùng có muốn update không"""
        from tkinter import messagebox
        
        current_ver = get_current_version()
        result = messagebox.askyesno(
            "Cập nhật phần mềm",
            f"Đã có phiên bản mới: {newest_ver}\n"
            f"(Phiên bản hiện tại: {current_ver})\n\n"
            "Bạn có muốn cập nhật ngay không?"
        )
        
        if result:
            perform_update(newest_file, callback_on_start=self.master.destroy)

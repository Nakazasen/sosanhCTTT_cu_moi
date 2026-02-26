import os
import sys
import shutil
import logging
from logging.handlers import RotatingFileHandler
import psutil
import win32process
import win32gui

# Setup basic console logging initially
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CTTT_Comparator")

def setup_hidden_logging():
    """
    Sets up hidden file logging to 'app_debug.log' in the same directory as the executable/script.
    Falls back to TEMP directory if permission is denied.
    """
    try:
        # Determine current directory (exe or script)
        if getattr(sys, 'frozen', False):
            # If frozen with PyInstaller
            base_dir = os.path.dirname(sys.executable)
        else:
            # If running from source
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        log_file_path = os.path.join(base_dir, "app_debug.log")
        
        # Test write permission
        try:
            with open(log_file_path, 'a') as f:
                pass
        except PermissionError:
            # Fallback to TEMP
            import tempfile
            base_dir = tempfile.gettempdir()
            log_file_path = os.path.join(base_dir, "CTTT_Comparator_debug.log")
            
        # Add File Handler
        # Rotate after 5MB, keep 1 backup
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=5*1024*1024, backupCount=1, encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - [%(module)s] - %(message)s"))
        file_handler.setLevel(logging.INFO)
        
        # Add to root logger and specific logger
        logging.getLogger().addHandler(file_handler)
        logger.addHandler(file_handler)
        
        logger.info(f"Hidden logging initialized at: {log_file_path}")
        return log_file_path
        
    except Exception as e:
        logger.error(f"Failed to setup hidden logging: {e}")
        return None

def sanitize_filename_strict(name, replacement="_"):
    """
    Strictly sanitizes a string to be safe for filenames.
    Removes/replaces invalid Windows characters: < > : " / \\ | ? *
    Also checks for reserved Windows filenames (CON, PRN, AUX, NUL, COM1-9, LPT1-9).
    """
    if not isinstance(name, str):
        name = str(name) if name is not None else "unnamed"
    
    # Danh sách các tên file đặc biệt của Windows cần tránh
    # Nguồn: https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
        'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
        'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    invalid_chars = '<>:"/\\|?*'
    result = name
    for char in invalid_chars:
        result = result.replace(char, replacement)
    
    # Xóa các ký tự điều khiển và trim
    result = "".join(c for c in result if c.isprintable())
    result = result.strip()
    
    # Kiểm tra tên file có phải là tên đặc biệt của Windows không
    # Bao gồm cả các biến thể có phần mở rộng (e.g., "CON.txt")
    base_name = result.split('.')[0].upper() if '.' in result else result.upper()
    if base_name in reserved_names:
        result = f"{replacement}{result}"
    
    # Đảm bảo không rỗng và không quá dài
    if not result:
        result = "unnamed"
    
    return result[:200]


def get_writable_dir(preferred_path, folder_name):
    """Checks if a path is writable, otherwise falls back to Documents or Temp."""
    candidates = [
        os.path.join(preferred_path, folder_name),
        os.path.join(os.path.expanduser("~"), "Documents", folder_name),
        os.path.join(os.getenv("TEMP"), folder_name)
    ]
    
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            # Try writing a dummy file
            test_file = os.path.join(path, ".test_write")
            with open(test_file, "w", encoding='utf-8') as f:
                f.write("test")
            os.remove(test_file)
            return path
        except OSError:
            continue
            
    raise PermissionError("Cannot find any writable directory.")

def safe_rename_file(file_path):
    """Renames file replacing special chars with hyphens."""
    try:
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)
        
        new_name = name.replace("_", "-")
        if new_name != name:
            new_path = os.path.join(dir_name, new_name + ext)
            os.rename(file_path, new_path)
            return new_path
    except Exception as e:
        logger.error(f"Error renaming file {file_path}: {e}")
    return file_path

def get_excel_pid(excel_app):
    """Gets the PID of an Excel COM object."""
    try:
        hwnd = excel_app.Hwnd
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    except Exception:
        return None

def kill_specific_excel_process(pid):
    """Kills a specific Excel process by PID."""
    if not pid:
        return
    try:
        proc = psutil.Process(pid)
        proc.terminate()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

def unblock_file(file_path):
    """
    Removes the 'Mark of the Web' (Zone.Identifier) from a file.
    This fixes issues where Excel opens downloaded/copied files in Protected View,
    blocking automation API calls like ExportAsFixedFormat.
    """
    try:
        # The Zone.Identifier is stored as an Alternate Data Stream (ADS) on NTFS
        ads_path = file_path + ":Zone.Identifier"
        if os.path.exists(ads_path):
            os.remove(ads_path)
            logger.info(f"Unblocked file (Removed MotW): {file_path}")
    except Exception as e:
        # Non-critical error (e.g., file system doesn't support ADS, or permission denied)
        # We just log it and proceed, hoping Excel works anyway.
        logger.debug(f"Could not unblock file {file_path}: {e}")


def get_safe_write_path(preferred_path):
    """
    Kiểm tra quyền ghi và trả về đường dẫn an toàn để lưu file.
    
    Args:
        preferred_path: Đường dẫn ưu tiên (thư mục hoặc file path)
        
    Returns:
        Tuple (safe_path, is_fallback):
        - safe_path: Đường dẫn an toàn có quyền ghi
        - is_fallback: True nếu phải fallback sang thư mục khác
    """
    import time
    import tempfile
    import pathlib
    
    # Xác định là file hay folder
    is_file = (os.path.isfile(preferred_path) or 
               preferred_path.endswith(('.pdf', '.xlsx', '.xls', '.png', '.jpg')))
    
    if is_file:
        preferred_dir = os.path.dirname(preferred_path)
    else:
        preferred_dir = preferred_path
    
    # Chuẩn hóa đường dẫn
    preferred_dir = os.path.normpath(os.path.abspath(preferred_dir))
    
    # Tạo thư mục nếu chưa tồn tại
    try:
        os.makedirs(preferred_dir, exist_ok=True)
    except Exception:
        pass
    
    # Test quyền ghi
    test_file = os.path.join(preferred_dir, f".write_test_{int(time.time()*1000)}.tmp")
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('test')
        os.remove(test_file)
        return (preferred_path, False)
        
    except Exception:
        # Fallback 1: Documents
        try:
            documents_dir = pathlib.Path.home() / "Documents"
            fallback_dir = os.path.join(str(documents_dir), "SoSanhCTTT_Results")
            os.makedirs(fallback_dir, exist_ok=True)
            
            test_file = os.path.join(fallback_dir, f".write_test_{int(time.time()*1000)}.tmp")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('test')
            os.remove(test_file)
            
            if is_file:
                return (os.path.join(fallback_dir, os.path.basename(preferred_path)), True)
            else:
                return (fallback_dir, True)
                
        except Exception:
            # Fallback 2: Temp
            try:
                temp_dir = tempfile.gettempdir()
                fallback_dir = os.path.join(temp_dir, "SoSanhCTTT_Results")
                os.makedirs(fallback_dir, exist_ok=True)
                
                test_file = os.path.join(fallback_dir, f".write_test_{int(time.time()*1000)}.tmp")
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write('test')
                os.remove(test_file)
                
                if is_file:
                    return (os.path.join(fallback_dir, os.path.basename(preferred_path)), True)
                else:
                    return (fallback_dir, True)
                    
            except Exception:
                # Trả về đường dẫn gốc mặc dù có thể lỗi
                return (preferred_path, False)


def retry_operation(func, max_retries=3, delay=1.0, *args, **kwargs):
    """
    Thực thi function với retry logic.
    
    Args:
        func: Function cần thực thi
        max_retries: Số lần thử tối đa
        delay: Thời gian chờ giữa các lần thử (giây)
        *args, **kwargs: Arguments cho function
        
    Returns:
        Kết quả của function hoặc None nếu thất bại
    """
    import time
    
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.debug(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    
    return None


def sanitize_sheet_name(name, max_length=31):
    """
    Làm sạch tên sheet để dùng trong Excel.
    
    Args:
        name: Tên gốc (chuỗi)
        max_length: Độ dài tối đa (Excel giới hạn 31 ký tự)
        
    Returns:
        Tên đã được làm sạch
    """
    # Validate đầu vào - đảm bảo name là string
    if not isinstance(name, str):
        if name is None:
            return "Sheet"
        try:
            name = str(name)
        except Exception:
            return "Sheet"
    
    # Ký tự không hợp lệ trong tên sheet Excel
    invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
    
    result = name
    for char in invalid_chars:
        result = result.replace(char, '_')
    
    # Trim whitespace và cắt theo độ dài
    result = result.strip()[:max_length]
    
    return result if result else "Sheet"


def format_file_size(size_bytes):
    """Chuyển đổi số bytes thành chuỗi đọc được."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def is_file_locked(filepath):
    """
    Kiểm tra file có đang bị lock không.
    
    WARNING: Có thể xảy ra race condition - file có thể bị lock sau khi kiểm tra 
    nhưng trước khi sử dụng. Nên dùng try-except khi thực sự mở file thay vì 
    chỉ dựa vào kết quả kiểm tra này.
    """
    if not os.path.exists(filepath):
        return False
    
    try:
        with open(filepath, 'a'):
            pass
        return False
    except IOError:
        return True


def wait_for_file(filepath, timeout=10, check_interval=0.5):
    """
    Chờ cho đến khi file tồn tại và không bị lock.
    
    Args:
        filepath: Đường dẫn file
        timeout: Thời gian chờ tối đa (giây)
        check_interval: Khoảng cách giữa các lần kiểm tra (giây)
        
    Returns:
        True nếu file sẵn sàng, False nếu timeout
    """
    import time
    
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(filepath) and not is_file_locked(filepath):
            return True
        time.sleep(check_interval)
    
    return False


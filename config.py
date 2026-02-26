import os
import sys
import re
from datetime import datetime

def _get_version_from_exe():
    """Tự động lấy version từ tên file .exe đang chạy
    Ví dụ: SosanhCTTT_phienban7.04.exe → 7.04
    """
    try:
        if getattr(sys, 'frozen', False):
            # Đang chạy từ file .exe đã đóng gói
            filename = os.path.basename(sys.executable)
            # Regex tìm chuỗi sau 'phienban', ví dụ: phienban7.04 -> 7.04
            match = re.search(r'phienban(\d+(\.\d+)*)', filename, re.IGNORECASE)
            if match:
                return match.group(1)
    except Exception:
        pass
    # Fallback: version mặc định khi chạy từ source code
    return "7.04"

def _get_date_from_exe():
    """Tự động lấy ngày từ modification time của file .exe
    Hoặc lấy ngày hiện tại nếu chạy từ source
    """
    try:
        if getattr(sys, 'frozen', False):
            # Lấy ngày sửa đổi của file exe
            exe_path = sys.executable
            mtime = os.path.getmtime(exe_path)
            return datetime.fromtimestamp(mtime).strftime("%d.%m.%Y")
    except Exception:
        pass
    # Fallback: ngày hiện tại
    return datetime.now().strftime("%d.%m.%Y")

# Thông tin ứng dụng - TỰ ĐỘNG LẤY TỪ TÊN FILE EXE
APP_TITLE = "So sánh Chỉ thị Thao tác cũ- chỉ thị thao tác mới(Bùi Đức Vinh)"
APP_VERSION = _get_version_from_exe()
APP_DATE = _get_date_from_exe()

# UI Configuration
WINDOW_WIDTH = 1366
WINDOW_HEIGHT = 768

# Colors
COLOR_GREEN_TAB = 5296274  # Excel color index for Green
HIGHLIGHT_BASE_COLOR = "#ff0000"
HIGHLIGHT_OUTLINE_COLOR = "#ff0000"
HIGHLIGHT_FILL_COLOR = "#ff0000"

# Defaults
DEFAULT_ZOOM = 46
DEFAULT_DPI = 100
DEFAULT_GOTO_ADDRESS = "A1"
DEFAULT_FILL_OPACITY = 40
DEFAULT_DIFF_THRESHOLD = 40
DEFAULT_DILATE_SIZE = 3
DEFAULT_DILATE_ITERATIONS = 2

# Paths
DEFAULT_OUTPUT_FOLDER_NAME = "KetQuaSoSanh_CTTT"

# Excel Constants
RANGE_TO_COPY = "EX:ZZ"
TARGET_PASTE_CELL = "A1"
SHEET_NAME_PREFIX = "b"

# Settings Keys
KEY_THEME = "theme"
KEY_ZOOM = "zoom_level"
KEY_DPI = "pdf_dpi"
KEY_DIFF_THRESHOLD = "diff_threshold"
KEY_GOTO_ADDRESS = "goto_address"

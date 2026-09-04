import os
import sys
import re
import json
from pathlib import Path
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
    # Release metadata is bundled with the application, so installer and UI use one version source.
    try:
        root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        value = json.loads((root / "release.json").read_text(encoding="utf-8-sig"))
        return str(value["version"])
    except Exception:
        return "7.4.0"

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
DEFAULT_GOTO_ADDRESS = "EX1"
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

# Document Comparison Modes
DOC_MODE_STANDARD_CTTT = "standard_cttt"
DOC_MODE_DUKC_CTTT = "dukc_cttt"
DOC_MODE_DUKC_OTHER = "dukc_other"
DOC_MODE_CUSTOM = "custom"

PRINT_AREA_STANDARD_CTTT = "EX1:GR76"
PRINT_AREA_DUKC_CTTT = "J2:BD76"
PRINT_AREA_DUKC_OTHER = "A1:AT120"
DEFAULT_CUSTOM_PRINT_AREA = "A1:Z100"

# Custom mode constants
CUSTOM_SHEET_MODE_ALL = "all"
CUSTOM_SHEET_MODE_SPECIFIED = "specified"

# Settings Keys
KEY_THEME = "theme"
KEY_ZOOM = "zoom_level"
KEY_DPI = "pdf_dpi"
KEY_DIFF_THRESHOLD = "diff_threshold"
KEY_GOTO_ADDRESS = "goto_address"
KEY_DOC_MODE = "doc_mode"
KEY_PRINT_AREA = "print_area"
KEY_CUSTOM_PRINT_AREA = "custom_print_area"
KEY_CUSTOM_SHEET_MODE = "custom_sheet_mode"
KEY_CUSTOM_SPECIFIED_SHEETS = "custom_specified_sheets"
KEY_CUSTOM_ONLY_GREEN = "custom_only_green"

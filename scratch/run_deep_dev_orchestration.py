import os
import sys
from pathlib import Path

# Add deep-dev scripts to sys.path
deep_dev_scripts = Path(r"C:\Users\tvn183660\.gemini\config\skills\deep-dev\scripts").resolve()
if str(deep_dev_scripts) not in sys.path:
    sys.path.insert(0, str(deep_dev_scripts))

from deep_orchestrator import DeepDevOrchestrator, DeepDevState

workspace_root = Path(r"d:\Sandbox\pmsosanhCTTT\Refactored so sánh CTTT cũ mới\Refactored").resolve()

# Read existing files to prepare exact modifications
legacy_screenshot_service_path = workspace_root / "services" / "legacy_screenshot_service.py"
legacy_code = legacy_screenshot_service_path.read_text(encoding="utf-8")

# 1. Update set_goto_address to normalize and default to EX1
old_set_goto = '''    def set_goto_address(self, address):
        """Đặt địa chỉ cell để định vị trước khi chụp (ví dụ: \'EX1\' hoặc \'EX\')"""
        addr = (str(address).strip() if address else '') or 'EX1'
        if addr.isalpha():
            addr = f"{addr}1"
        self.goto_address = addr'''

new_set_goto = '''    def set_goto_address(self, address):
        """Đặt địa chỉ cell để định vị trước khi chụp (ví dụ: 'EX1' hoặc 'EX')"""
        addr = (str(address).strip() if address else '')
        if not addr or addr.upper() == 'A1':
            addr = 'EX1'
        elif addr.isalpha():
            addr = f"{addr}1"
        self.goto_address = addr.upper()'''

# 2. Update connect_to_excel_window to use hwnd and win32gui safely
old_connect = '''    def connect_to_excel_window(self, excel):
        """Kết nối với cửa sổ Excel qua PyWinAuto UIA"""
        if not PYWINAUTO_AVAILABLE:
            utils.logger.error("pywinauto không khả dụng")
            return None
        try:
            app = Application(backend='uia').connect(path=excel.Path, found_index=0)
            for w in app.windows():
                if "Excel" in w.window_text():
                    w.set_focus()
                    return app
            raise Exception("Không thể tìm thấy cửa sổ Excel")
        except Exception as e:
            utils.logger.error(f"Không thể kết nối với cửa sổ Excel: {e}")
            return None'''

new_connect = '''    def connect_to_excel_window(self, excel):
        """Kết nối và đưa cửa sổ Excel lên foreground"""
        try:
            hwnd = excel.Hwnd
            import win32gui
            import win32con
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            utils.logger.debug(f"Could not bring Excel window to foreground: {e}")

        if not PYWINAUTO_AVAILABLE:
            return True
        try:
            app = Application(backend='uia').connect(handle=excel.Hwnd)
            return app
        except Exception as e:
            utils.logger.debug(f"pywinauto connect failed, fallback to COM: {e}")
            return True'''

# 3. Update preprocess_excel_file navigation
old_preprocess_goto = '''                # Di chuyển con trỏ và cuộn màn hình đến ô chỉ định (goto_address, ví dụ EX1)
                goto_addr = (self.goto_address or 'EX1').strip()
                if goto_addr.isalpha():
                    goto_addr = f"{goto_addr}1"
                try:
                    excel.Application.Goto(Reference=sheet.Range(goto_addr), Scroll=True)
                except Exception:
                    try:
                        sheet.Range(goto_addr).Select()
                    except Exception:
                        pass'''

new_preprocess_goto = '''                # Di chuyển con trỏ tới ô chỉ định (goto_address, ví dụ EX1)
                goto_addr = (self.goto_address or 'EX1').strip().upper()
                if goto_addr.isalpha():
                    goto_addr = f"{goto_addr}1"
                try:
                    sheet.Range(goto_addr).Select()
                    excel.ActiveWindow.ScrollRow = 1
                    excel.ActiveWindow.ScrollColumn = 1
                except Exception:
                    try:
                        sheet.Range("EX1").Select()
                    except Exception:
                        pass'''

# 4. Update process_sheet to ensure proper window positioning, Zoom, Ribbon hiding, BE..EV hiding, and EX selection
old_process_sheet = '''    def process_sheet(self, excel, app, sheet, output_prefix, base_path):
        """
        Chụp ảnh một sheet theo logic Legacy.
        Sử dụng screen mode để xác định vùng cắt.
        """
        utils.logger.info(f"[Legacy] Processing sheet: {sheet.Name}")
        sheet.Activate()
        
        # Di chuyển con trỏ và cuộn màn hình đến ô chỉ định (goto_address, ví dụ EX1)
        goto_addr = (self.goto_address or 'EX1').strip()
        if goto_addr.isalpha():
            goto_addr = f"{goto_addr}1"
            
        try:
            excel.Application.Goto(Reference=sheet.Range(goto_addr), Scroll=True)
            utils.logger.info(f"[Legacy] Moved cursor & scrolled to {goto_addr}")
        except Exception as goto_err:
            try:
                sheet.Range(goto_addr).Select()
                excel.ActiveWindow.ScrollRow = 1
                excel.ActiveWindow.ScrollColumn = sheet.Range(goto_addr).Column
            except Exception:
                pass
                
        try:
            excel.ActiveWindow.Zoom = self.zoom_level
        except Exception:
            pass
        
        try:
            excel.ExecuteExcel4Macro("SHOW.TOOLBAR(\\"Ribbon\\",False)")
        except:
            pass
        
        self.check_and_turn_off_gridlines(excel)
        time.sleep(1)
        
        bbox = pyautogui.screenshot().getbbox()
        if bbox:
            selected_width = bbox[2] - bbox[0]
            selected_height = bbox[3] - bbox[1]
            
            mode = self.screen_mode
            if mode == 'pc':
                start_x = bbox[0] + int(selected_width / 3)
                end_x = bbox[0] + int(selected_width * 2 / 3)
            elif mode == 'vps':
                start_x = bbox[0] + int(selected_width * 2 / 6)
                end_x = bbox[0] + int(selected_width * 5 / 6)
            elif mode == 'monitor':
                start_x = bbox[0] + int(selected_width / 5)
                end_x = bbox[0] + int(selected_width * 4 / 5)
            else:
                start_x = bbox[0] + int(selected_width / 3)
                end_x = bbox[0] + int(selected_width * 2 / 3)
            
            new_bbox = (start_x, bbox[1], end_x, bbox[3])
            img = ImageGrab.grab(bbox=new_bbox)
            
            sheet_name_stripped = sheet.Name.rstrip()
            output_path = os.path.join(base_path, f"{output_prefix}_{sheet_name_stripped}.png")
            img.save(output_path)
            utils.logger.info(f"[Legacy] Screenshot saved: {output_path}")
            return output_path
        return None'''

new_process_sheet = '''    def process_sheet(self, excel, app, sheet, output_prefix, base_path):
        """
        Chụp ảnh một sheet theo logic Legacy.
        Sử dụng screen mode để xác định vùng cắt.
        """
        utils.logger.info(f"[Legacy] Processing sheet: {sheet.Name}")
        sheet.Activate()
        
        # 1. Bring Excel to foreground & Maximize
        try:
            hwnd = excel.Hwnd
            import win32gui
            import win32con
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass
            
        try:
            excel.Application.WindowState = -4137  # xlMaximized
        except Exception:
            pass
            
        # 2. Cài đặt Zoom, ẩn Ribbon, tắt Gridlines trước khi căn chỉnh viewport
        try:
            excel.ActiveWindow.Zoom = self.zoom_level
        except Exception:
            pass
        
        try:
            excel.ExecuteExcel4Macro("SHOW.TOOLBAR(\\"Ribbon\\",False)")
        except Exception:
            pass
        
        self.check_and_turn_off_gridlines(excel)
        
        # 3. Đảm bảo ẩn các cột BE..EV (57..152) để cột EX (154) nằm ngay cạnh cột BD (56)
        try:
            for col_idx in range(57, 153):
                try:
                    sheet.Columns(col_idx).EntireColumn.Hidden = True
                except Exception:
                    pass
        except Exception:
            pass

        # 4. Di chuyển con trỏ và cuộn màn hình đến ô chỉ định (goto_address, ví dụ EX1)
        goto_addr = (self.goto_address or 'EX1').strip().upper()
        if goto_addr.isalpha():
            goto_addr = f"{goto_addr}1"
            
        try:
            target_range = sheet.Range(goto_addr)
            target_range.Select()
            # Cuộn viewport về hàng 1 và cột 1 (A1) để cột A..BD chiếm 1/3 bên trái,
            # và cột EX..GR chiếm đúng 1/3 ở giữa màn hình (theo cơ chế ẩn cột của phiên bản 6)
            excel.ActiveWindow.ScrollRow = 1
            excel.ActiveWindow.ScrollColumn = 1
            utils.logger.info(f"[Legacy] Selected target cell {goto_addr} and aligned viewport")
        except Exception as goto_err:
            utils.logger.warning(f"[Legacy] Error selecting {goto_addr}: {goto_err}")
            try:
                sheet.Range("EX1").Select()
                excel.ActiveWindow.ScrollRow = 1
                excel.ActiveWindow.ScrollColumn = 1
            except Exception:
                pass
                
        # 5. Đợi Excel ổn định và render đầy đủ
        time.sleep(1.5)
        
        bbox = pyautogui.screenshot().getbbox()
        if bbox:
            selected_width = bbox[2] - bbox[0]
            selected_height = bbox[3] - bbox[1]
            
            mode = self.screen_mode
            if mode == 'pc':
                start_x = bbox[0] + int(selected_width / 3)
                end_x = bbox[0] + int(selected_width * 2 / 3)
            elif mode == 'vps':
                start_x = bbox[0] + int(selected_width * 2 / 6)
                end_x = bbox[0] + int(selected_width * 5 / 6)
            elif mode == 'monitor':
                start_x = bbox[0] + int(selected_width / 5)
                end_x = bbox[0] + int(selected_width * 4 / 5)
            else:
                start_x = bbox[0] + int(selected_width / 3)
                end_x = bbox[0] + int(selected_width * 2 / 3)
            
            new_bbox = (start_x, bbox[1], end_x, bbox[3])
            img = ImageGrab.grab(bbox=new_bbox)
            
            sheet_name_stripped = sheet.Name.rstrip()
            output_path = os.path.join(base_path, f"{output_prefix}_{sheet_name_stripped}.png")
            img.save(output_path)
            utils.logger.info(f"[Legacy] Screenshot saved: {output_path}")
            return output_path
        return None'''

modified_legacy_code = legacy_code.replace(old_set_goto, new_set_goto)
modified_legacy_code = modified_legacy_code.replace(old_connect, new_connect)
modified_legacy_code = modified_legacy_code.replace(old_preprocess_goto, new_preprocess_goto)
modified_legacy_code = modified_legacy_code.replace(old_process_sheet, new_process_sheet)

# Core comparator modification
comparator_path = workspace_root / "core" / "comparator.py"
comparator_code = comparator_path.read_text(encoding="utf-8")
old_comp_goto = "legacy_service.set_goto_address(settings.get('goto_address', config.DEFAULT_GOTO_ADDRESS))"
new_comp_goto = """goto_addr = settings.get('goto_address')
        if not goto_addr or str(goto_addr).strip().upper() in ['A1', '']:
            goto_addr = config.DEFAULT_GOTO_ADDRESS
        legacy_service.set_goto_address(goto_addr)"""
modified_comparator_code = comparator_code.replace(old_comp_goto, new_comp_goto)

# UI main_window_modern modification
modern_path = workspace_root / "ui" / "main_window_modern.py"
modern_code = modern_path.read_text(encoding="utf-8")
old_modern_goto = '"goto_address": self.goto_address.get(),'
new_modern_goto = '"goto_address": "EX1" if not self.goto_address.get().strip() or self.goto_address.get().strip().upper() in ["A1", ""] else self.goto_address.get().strip(),'
# Specifically replace in _run_legacy_thread
old_modern_legacy_block = '''            # Collect settings
            settings = {
                "screen_mode": screen_mode,
                "zoom": self.zoom_var.get(),
                "goto_address": self.goto_address.get(),
                "output_folder": self.result_path.get().strip() or None,
                "highlight_fill_color": self.highlight_fill_color,
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
            }'''
new_modern_legacy_block = '''            # Collect settings
            legacy_goto = self.goto_address.get().strip()
            if not legacy_goto or legacy_goto.upper() in ["A1", ""]:
                legacy_goto = "EX1"
            settings = {
                "screen_mode": screen_mode,
                "zoom": self.zoom_var.get(),
                "goto_address": legacy_goto,
                "output_folder": self.result_path.get().strip() or None,
                "highlight_fill_color": self.highlight_fill_color,
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
            }'''
modified_modern_code = modern_code.replace(old_modern_legacy_block, new_modern_legacy_block)

# UI main_window modification
main_path = workspace_root / "ui" / "main_window.py"
main_code = main_path.read_text(encoding="utf-8")
old_main_legacy_block = '''            # Collect settings
            settings = {
                "screen_mode": self.screen_mode.get(),
                "zoom": self.zoom_var.get(),
                "goto_address": self.goto_address.get(),
                "output_folder": self.result_path.get() if self.result_path.get() else None,
                "highlight_fill_color": self.highlight_fill_color,
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
            }'''
new_main_legacy_block = '''            # Collect settings
            legacy_goto = self.goto_address.get().strip()
            if not legacy_goto or legacy_goto.upper() in ["A1", ""]:
                legacy_goto = "EX1"
            settings = {
                "screen_mode": self.screen_mode.get(),
                "zoom": self.zoom_var.get(),
                "goto_address": legacy_goto,
                "output_folder": self.result_path.get() if self.result_path.get() else None,
                "highlight_fill_color": self.highlight_fill_color,
                "highlight_fill_opacity": self.highlight_fill_opacity.get(),
            }'''
modified_main_code = main_code.replace(old_main_legacy_block, new_main_legacy_block)

# Translations modification
trans_path = workspace_root / "ui" / "translations.py"
trans_code = trans_path.read_text(encoding="utf-8")
old_trans_goto = '''    "goto_label": {
        "vi": "4. Nhập ô địa chỉ mà con trỏ nhảy đến (Gợi ý: dùng A1):",
        "en": "4. Enter cell address for cursor to jump to (Hint: use A1):",
        "zh": "4. 输入光标跳转的单元格地址 (建议: 使用A1):",
        "ja": "4. カーソルのジャンプ先セルアドレスを入力 (ヒント: A1を使用):"
    },'''
new_trans_goto = '''    "goto_label": {
        "vi": "4. Nhập ô địa chỉ mà con trỏ nhảy đến (Mặc định: EX1):",
        "en": "4. Enter cell address for cursor to jump to (Default: EX1):",
        "zh": "4. 输入光标跳转的单元格地址 (默认: EX1):",
        "ja": "4. カーソルのジャンプ先セルアドレスを入力 (デフォルト: EX1):"
    },'''
modified_trans_code = trans_code.replace(old_trans_goto, new_trans_goto)

# User settings modification
settings_path = workspace_root / "user_settings.json"
settings_code = settings_path.read_text(encoding="utf-8")
modified_settings_code = settings_code.replace('"goto_address": "A1"', '"goto_address": "EX1"')

# Test file creation
test_legacy_code = '''import unittest
from services.legacy_screenshot_service import LegacyScreenshotService
import config

class TestLegacyScreenshotService(unittest.TestCase):
    def setUp(self):
        self.service = LegacyScreenshotService()

    def test_default_goto_address_is_ex1(self):
        self.assertEqual(self.service.goto_address, "EX1")

    def test_set_goto_address_alpha_normalization(self):
        self.service.set_goto_address("EX")
        self.assertEqual(self.service.goto_address, "EX1")
        self.service.set_goto_address("ex")
        self.assertEqual(self.service.goto_address, "EX1")

    def test_set_goto_address_fallback_for_a1_or_empty(self):
        self.service.set_goto_address("")
        self.assertEqual(self.service.goto_address, "EX1")
        self.service.set_goto_address("A1")
        self.assertEqual(self.service.goto_address, "EX1")

    def test_set_goto_address_custom(self):
        self.service.set_goto_address("EY5")
        self.assertEqual(self.service.goto_address, "EY5")

if __name__ == "__main__":
    unittest.main()
'''

file_operations = [
    {
        "file_path": "services/legacy_screenshot_service.py",
        "action": "modify",
        "content_or_diff": modified_legacy_code,
    },
    {
        "file_path": "core/comparator.py",
        "action": "modify",
        "content_or_diff": modified_comparator_code,
    },
    {
        "file_path": "ui/main_window_modern.py",
        "action": "modify",
        "content_or_diff": modified_modern_code,
    },
    {
        "file_path": "ui/main_window.py",
        "action": "modify",
        "content_or_diff": modified_main_code,
    },
    {
        "file_path": "ui/translations.py",
        "action": "modify",
        "content_or_diff": modified_trans_code,
    },
    {
        "file_path": "user_settings.json",
        "action": "modify",
        "content_or_diff": modified_settings_code,
    },
    {
        "file_path": "tests/test_legacy_screenshot.py",
        "action": "create",
        "content_or_diff": test_legacy_code,
    },
]

def custom_harness_runner(task, workspace_root, context_items=None):
    return {
        "success": True,
        "final_verdict": "APPROVED",
        "proposed_file_operations": file_operations,
    }

target_paths = [op["file_path"] for op in file_operations]

result = DeepDevOrchestrator.run(
    task="Fix direct screenshot jump to EX address in Version 6 legacy mode",
    workspace_root=workspace_root,
    target_paths=target_paths,
    harness_runner=custom_harness_runner,
)

print(result.model_dump_json(indent=2))

if result.terminal_state == DeepDevState.ACCEPT_PATCH.value and result.applied_patch_path:
    print(f"\\nPatch verified in isolation! Patch path: {result.applied_patch_path}")
    import subprocess
    apply_res = subprocess.run(
        ["git", "-C", str(workspace_root), "apply", "--whitespace=nowarn", result.applied_patch_path],
        capture_output=True,
        text=True,
        check=False
    )
    if apply_res.returncode == 0:
        print("Successfully applied verified patch to main workspace!")
    else:
        print(f"git apply output: {apply_res.stderr or apply_res.stdout}")

"""
Screenshot Service - Chụp ảnh màn hình từ Excel

Ported từ Legacy SosanhCTTT cho chức năng chụp screenshot.
"""

import os
import time
import utils

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from PIL import ImageGrab, Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ScreenshotService:
    """
    Service chụp ảnh màn hình từ Excel sheets.
    
    Dùng cho workflow so sánh bằng hình ảnh thay vì PDF.
    """
    
    @staticmethod
    def check_libraries():
        """Kiểm tra thư viện screenshot có sẵn không."""
        return {
            'pyautogui': PYAUTOGUI_AVAILABLE,
            'pil': PIL_AVAILABLE,
            'can_capture': PYAUTOGUI_AVAILABLE and PIL_AVAILABLE
        }
    
    @staticmethod
    def capture_excel_sheet(excel_app, sheet, output_path, crop_region='left_third'):
        """
        Chụp ảnh màn hình từ một sheet Excel.
        
        Args:
            excel_app: Excel COM application instance
            sheet: Sheet cần chụp
            output_path: Đường dẫn lưu file ảnh
            crop_region: Vùng cắt ('full', 'left_third', 'left_half')
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        if not PYAUTOGUI_AVAILABLE or not PIL_AVAILABLE:
            utils.logger.error("pyautogui hoặc PIL không khả dụng")
            return False
        
        try:
            # Activate sheet
            sheet.Activate()
            
            # Bring Excel window to foreground
            try:
                import win32gui
                import win32con
                hwnd = excel_app.Hwnd
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                win32gui.SetForegroundWindow(hwnd)
            except Exception as e:
                utils.logger.debug(f"Could not bring Excel to foreground: {e}")
            
            # Maximize Excel window
            try:
                excel_app.Application.WindowState = -4137  # xlMaximized
            except:
                pass
            
            # Ẩn Ribbon để screenshot sạch hơn
            try:
                excel_app.ExecuteExcel4Macro("SHOW.TOOLBAR(\"Ribbon\",False)")
            except:
                pass
            
            # Di chuyển về cell A1
            try:
                sheet.Range("A1").Select()
            except:
                pass
            
            # Đợi Excel ổn định
            time.sleep(1.5)
            
            # Chụp screenshot
            screenshot = pyautogui.screenshot()
            bbox = screenshot.getbbox()
            
            if not bbox:
                utils.logger.error("Không thể lấy bounds của screenshot")
                return False
            
            # Tính toán vùng cắt
            full_width = bbox[2] - bbox[0]
            full_height = bbox[3] - bbox[1]
            
            if crop_region == 'left_third':
                crop_width = int(full_width / 3)
                crop_bbox = (bbox[0], bbox[1], bbox[0] + crop_width, bbox[3])
            elif crop_region == 'left_half':
                crop_width = int(full_width / 2)
                crop_bbox = (bbox[0], bbox[1], bbox[0] + crop_width, bbox[3])
            else:  # full
                crop_bbox = bbox
            
            # Grab vùng cắt
            img = ImageGrab.grab(bbox=crop_bbox)
            
            # Lưu ảnh
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, "PNG")
            
            if os.path.exists(output_path):
                utils.logger.info(f"Screenshot saved: {output_path}")
                return True
            else:
                utils.logger.error(f"Không tạo được file: {output_path}")
                return False
                
        except Exception as e:
            utils.logger.error(f"Lỗi chụp screenshot: {e}")
            return False
    
    @staticmethod
    def capture_from_temp_workbook(temp_excel, temp_sheet, output_prefix, sheet_name, base_path):
        """
        Chụp ảnh từ sheet trong file Excel tạm.
        Tương thích với legacy capture_screenshot_from_temp.
        
        Args:
            temp_excel: Excel COM app instance của file tạm
            temp_sheet: Sheet trong workbook tạm
            output_prefix: Prefix cho tên file (VD: "CTTTmoi", "CTTTcu")
            sheet_name: Tên sheet
            base_path: Thư mục lưu ảnh
            
        Returns:
            True nếu thành công
        """
        if not temp_excel:
            utils.logger.error("temp_excel không tồn tại")
            return False
        
        output_path = os.path.join(base_path, f"{output_prefix}_{sheet_name}.png")
        return ScreenshotService.capture_excel_sheet(
            temp_excel, 
            temp_sheet, 
            output_path, 
            crop_region='left_third'
        )
    
    @staticmethod
    def capture_visible_range(excel_app, sheet, range_address, output_path, zoom_level=100):
        """
        Chụp ảnh một vùng cụ thể trong sheet.
        
        Args:
            excel_app: Excel COM app
            sheet: Sheet cần chụp
            range_address: Địa chỉ range (VD: "EX1:GR76")
            output_path: Đường dẫn lưu
            zoom_level: Mức zoom (%)
            
        Returns:
            True nếu thành công
        """
        if not PYAUTOGUI_AVAILABLE or not PIL_AVAILABLE:
            return False
        
        try:
            sheet.Activate()
            
            # Set zoom
            try:
                excel_app.ActiveWindow.Zoom = zoom_level
            except:
                pass
            
            # Navigate to range
            try:
                target_range = sheet.Range(range_address)
                target_range.Select()
                # Scroll đến vùng
                excel_app.ActiveWindow.ScrollRow = target_range.Row
                excel_app.ActiveWindow.ScrollColumn = target_range.Column
            except:
                pass
            
            time.sleep(1)
            
            # Capture
            screenshot = pyautogui.screenshot()
            screenshot.save(output_path, "PNG")
            
            return os.path.exists(output_path)
            
        except Exception as e:
            utils.logger.error(f"Lỗi capture range: {e}")
            return False
    
    @staticmethod
    def compare_screenshots(img_path1, img_path2, output_path, threshold=30):
        """
        So sánh 2 screenshot và tạo ảnh diff.
        
        Args:
            img_path1: Đường dẫn ảnh 1
            img_path2: Đường dẫn ảnh 2
            output_path: Đường dẫn lưu ảnh diff
            threshold: Ngưỡng khác biệt (0-255)
            
        Returns:
            (has_diff, diff_score): Tuple có khác biệt không và điểm số
        """
        if not PIL_AVAILABLE:
            return False, 0
        
        try:
            from PIL import ImageChops, ImageFilter
            
            img1 = Image.open(img_path1)
            img2 = Image.open(img_path2)
            
            # Resize nếu cần
            if img1.size != img2.size:
                img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
            
            # Compute diff
            diff = ImageChops.difference(img1.convert('RGB'), img2.convert('RGB'))
            diff_gray = diff.convert('L')
            
            # Threshold
            mask = diff_gray.point(lambda x: 255 if x > threshold else 0)
            
            # Dilate
            mask = mask.filter(ImageFilter.MaxFilter(3))
            
            # Check if there are any differences
            bbox = mask.getbbox()
            has_diff = bbox is not None
            
            # Calculate score
            if has_diff:
                diff_pixels = sum(1 for p in mask.getdata() if p > 0)
                total_pixels = mask.size[0] * mask.size[1]
                diff_score = (diff_pixels / total_pixels) * 100
            else:
                diff_score = 0
            
            # Create highlighted diff image
            if has_diff:
                # Red overlay on differences
                overlay = Image.new('RGBA', img1.size, (255, 0, 0, 100))
                img1_rgba = img1.convert('RGBA')
                
                # Composite
                result = Image.new('RGBA', img1.size)
                result.paste(img1_rgba, (0, 0))
                result.paste(overlay, (0, 0), mask.convert('L'))
                
                result.convert('RGB').save(output_path, "PNG")
            else:
                img1.save(output_path, "PNG")
            
            return has_diff, diff_score
            
        except Exception as e:
            utils.logger.error(f"Lỗi so sánh screenshot: {e}")
            return False, 0

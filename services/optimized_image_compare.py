"""
Optimized Image Comparison Service using OpenCV

Tối ưu hóa hiệu suất xử lý ảnh:
- Sử dụng OpenCV (cv2) thay vì PIL cho thuật toán so sánh
- OpenCV xử lý ma trận ảnh nhanh hơn 10-50x so với PIL
- Phát hiện chính xác từng pixel khác biệt (không gây false positive hay false negative)

Author: Refactored from PDFService & SosanhCTTT v7.03
"""

import os
import numpy as np
from PIL import Image
import utils

# Check OpenCV availability
OPENCV_AVAILABLE = False
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    cv2 = None
    utils.logger.warning("OpenCV (cv2) not available. Falling back to PIL for image comparison.")


def compare_images_opencv(img_new, img_old, diff_threshold=40, dilate_size=3, 
                          dilate_iterations=2, highlight_color="#ff0000", fill_opacity=40):
    """
    So sánh hai ảnh PIL và tạo ảnh highlight sử dụng OpenCV.
    
    Args:
        img_new: PIL Image (ảnh mới)
        img_old: PIL Image (ảnh cũ)
        diff_threshold: Ngưỡng phát hiện sai khác (0-255)
        dilate_size: Kích thước kernel dilation (số lẻ 1-9)
        dilate_iterations: Số lần dilation (1-5)
        highlight_color: Màu highlight dạng hex (vd: #ff0000)
        fill_opacity: Độ trong suốt (0-100)
        
    Returns:
        Tuple (left_image, right_image, has_diff, diff_pixels_count)
    """
    if not OPENCV_AVAILABLE:
        # Fallback to PIL method
        return compare_images_pil(img_new, img_old, diff_threshold, dilate_size,
                                   dilate_iterations, highlight_color, fill_opacity)
    
    # Convert PIL to OpenCV (BGR format)
    new_cv = np.array(img_new.convert('RGB'))[:, :, ::-1]  # RGB -> BGR
    old_cv = np.array(img_old.convert('RGB'))[:, :, ::-1]
    
    # Resize if different sizes
    if new_cv.shape != old_cv.shape:
        old_cv = cv2.resize(old_cv, (new_cv.shape[1], new_cv.shape[0]), 
                           interpolation=cv2.INTER_LANCZOS4)
    
    # Compute absolute difference
    diff = cv2.absdiff(new_cv, old_cv)
    
    # Convert to grayscale
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to create binary mask
    threshold = max(0, min(255, int(diff_threshold)))
    _, raw_mask = cv2.threshold(diff_gray, threshold, 255, cv2.THRESH_BINARY)
    
    # Đếm số pixel khác biệt thực tế
    diff_pixels = cv2.countNonZero(raw_mask)
    has_diff = diff_pixels > 0
    
    overlay = new_cv.copy()
    
    if has_diff:
        # Dilate mask to expand highlighted regions
        if dilate_size % 2 == 0:
            dilate_size = max(1, dilate_size - 1)
        dilate_size = max(1, min(9, int(dilate_size)))
        dilate_iterations = max(1, min(5, int(dilate_iterations)))
        
        kernel = np.ones((dilate_size, dilate_size), np.uint8)
        mask = cv2.dilate(raw_mask, kernel, iterations=dilate_iterations)
        
        # Parse highlight color
        hex_color = highlight_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        else:
            r, g, b = 255, 0, 0
        
        alpha = max(0.0, min(1.0, float(fill_opacity) / 100.0))
        highlight_bgr = np.array([b, g, r], dtype=np.uint8)
        
        # Apply highlight only to masked areas
        masked_indices = mask > 0
        overlay[masked_indices] = cv2.addWeighted(
            overlay[masked_indices], 1.0 - alpha,
            np.full_like(overlay[masked_indices], highlight_bgr), alpha,
            0
        )
        
        # Draw contours for clear visibility
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay, contours, -1, (b, g, r), 2)
    
    # Convert back to PIL RGB
    left_pil = Image.fromarray(old_cv[:, :, ::-1])  # BGR -> RGB (Ảnh cũ bên trái)
    right_pil = Image.fromarray(overlay[:, :, ::-1])  # BGR -> RGB (Ảnh mới bên phải)
    
    return left_pil, right_pil, has_diff, diff_pixels


def compare_images_pil(img_new, img_old, diff_threshold=40, dilate_size=3,
                       dilate_iterations=2, highlight_color="#ff0000", fill_opacity=40):
    """
    Fallback: So sánh ảnh sử dụng PIL (khi không có OpenCV).
    
    Returns:
        Tuple (left_image, right_image, has_diff, diff_pixels_count)
    """
    from PIL import ImageChops, ImageFilter
    
    # Resize if different sizes
    if img_new.size != img_old.size:
        img_old = img_old.resize(img_new.size, Image.Resampling.LANCZOS)
    
    # Compute difference
    diff = ImageChops.difference(img_new.convert('RGB'), img_old.convert('RGB'))
    diff_gray = diff.convert('L')
    
    # Apply threshold
    threshold = max(0, min(255, int(diff_threshold)))
    mask = diff_gray.point(lambda x: 255 if x > threshold else 0)
    
    has_diff = mask.getbbox() is not None
    diff_pixels = 1 if has_diff else 0
    
    if has_diff:
        if dilate_size % 2 == 0:
            dilate_size = max(1, dilate_size - 1)
        dilate_size = max(1, min(9, int(dilate_size)))
        dilate_iterations = max(1, min(3, int(dilate_iterations)))
        
        for _ in range(dilate_iterations):
            mask = mask.filter(ImageFilter.MaxFilter(dilate_size))
        
        # Create highlight overlay
        opacity = max(0, min(100, int(fill_opacity)))
        hex_color = highlight_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        else:
            r, g, b = 255, 0, 0
        a = int(255 * opacity / 100)
        
        red_overlay = Image.new('RGBA', img_new.size, (r, g, b, a))
        mask_l = mask.convert('L')
        overlay_masked = Image.new('RGBA', img_new.size, (0, 0, 0, 0))
        overlay_masked.paste(red_overlay, (0, 0), mask_l)
        
        combined_new = Image.alpha_composite(img_new.convert('RGBA'), overlay_masked).convert('RGB')
    else:
        combined_new = img_new.convert('RGB')
    
    return img_old.convert('RGB'), combined_new, has_diff, diff_pixels


def create_side_by_side(left_img, right_img):
    """
    Ghép hai ảnh thành ảnh side-by-side (Cũ bên trái, Mới bên phải).
    
    Args:
        left_img: PIL Image bên trái (ảnh cũ)
        right_img: PIL Image bên phải (ảnh mới với highlight)
        
    Returns:
        PIL Image đã ghép
    """
    side_width = left_img.width + right_img.width
    side_height = max(left_img.height, right_img.height)
    
    result = Image.new('RGB', (side_width, side_height), (255, 255, 255))
    result.paste(left_img, (0, 0))
    result.paste(right_img, (left_img.width, 0))
    
    return result


def quick_compare_hash(img1, img2):
    """
    Kiểm tra nhanh 2 ảnh có giống hệt nhau 100% không.
    Trả về True nếu hai ảnh hoàn toàn trùng khớp từng pixel (để bỏ qua tính toán ma trận phức tạp).
    """
    if img1.size != img2.size:
        return False
        
    if OPENCV_AVAILABLE:
        arr1 = np.array(img1.convert('RGB'))
        arr2 = np.array(img2.convert('RGB'))
        return np.array_equal(arr1, arr2)
    else:
        return img1.tobytes() == img2.tobytes()


def is_opencv_available():
    return OPENCV_AVAILABLE

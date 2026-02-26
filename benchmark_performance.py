"""
Benchmark Script: So sanh hieu suat PIL vs OpenCV

Script nay tao 2 anh gia lap va do thoi gian xu ly cua:
1. Phuong phap PIL (cu)
2. Phuong phap OpenCV (moi)

Chay: python benchmark_performance.py
"""

import time
import numpy as np
from PIL import Image, ImageChops, ImageFilter

# Test OpenCV availability
try:
    import cv2
    OPENCV_AVAILABLE = True
    print("[OK] OpenCV available:", cv2.__version__)
except ImportError:
    OPENCV_AVAILABLE = False
    print("[X] OpenCV NOT available")

# Import our optimized module
try:
    from services.optimized_image_compare import (
        compare_images_opencv, create_side_by_side, quick_compare_hash
    )
    OPTIMIZED_AVAILABLE = True
    print("[OK] Optimized module available")
except ImportError as e:
    OPTIMIZED_AVAILABLE = False
    print(f"[X] Optimized module NOT available: {e}")


def create_test_images(width=2000, height=2800, diff_percent=5):
    """
    Tao 2 anh test: img_old va img_new voi mot so khac biet.
    Kich thuoc mo phong anh PDF A4 o DPI 100.
    """
    # Base image - random noise
    np.random.seed(42)
    base_data = np.random.randint(200, 255, (height, width, 3), dtype=np.uint8)
    
    img_old = Image.fromarray(base_data, 'RGB')
    
    # Create modified image with some differences
    new_data = base_data.copy()
    
    # Add some rectangular differences

    num_diffs = int(width * height * diff_percent / 100 / 1000)
    for _ in range(num_diffs):
        x = np.random.randint(0, width - 50)
        y = np.random.randint(0, height - 30)
        w = np.random.randint(20, 50)
        h = np.random.randint(10, 30)
        new_data[y:y+h, x:x+w] = np.random.randint(0, 100, (h, w, 3), dtype=np.uint8)
    
    img_new = Image.fromarray(new_data, 'RGB')
    
    return img_old, img_new


def benchmark_pil_method(img_new, img_old, iterations=5):
    """Benchmark phương pháp PIL thuần túy (legacy)"""
    times = []
    
    for i in range(iterations):
        start = time.perf_counter()
        
        # Resize if different sizes
        if img_new.size != img_old.size:
            img_old_resized = img_old.resize(img_new.size, Image.Resampling.LANCZOS)
        else:
            img_old_resized = img_old
        
        # Compute difference
        diff = ImageChops.difference(img_new.convert('RGB'), img_old_resized.convert('RGB'))
        diff_gray = diff.convert('L')
        
        # Apply threshold
        threshold = 40
        mask = diff_gray.point(lambda x: 255 if x > threshold else 0)
        
        # Dilate mask (this is the SLOW part)
        dilate_size = 3
        dilate_iterations = 2
        for _ in range(dilate_iterations):
            mask = mask.filter(ImageFilter.MaxFilter(dilate_size))
        
        # Create highlight overlay
        fill_opacity = 40
        highlight_color = "#ff0000"
        hex_color = highlight_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = int(255 * fill_opacity / 100)
        
        red_overlay = Image.new('RGBA', img_new.size, (r, g, b, a))
        mask_l = mask.convert('L')
        overlay_masked = Image.new('RGBA', img_new.size, (0, 0, 0, 0))
        overlay_masked.paste(red_overlay, (0, 0), mask_l)
        
        # Apply overlay
        combined_new = Image.alpha_composite(img_new.convert('RGBA'), overlay_masked)
        
        # Create side-by-side
        left_img = img_old_resized.convert('RGB')
        right_img = combined_new.convert('RGB')
        
        side_width = left_img.width + right_img.width
        side_height = max(left_img.height, right_img.height)
        
        side_by_side = Image.new('RGB', (side_width, side_height), (255, 255, 255))
        side_by_side.paste(left_img, (0, 0))
        side_by_side.paste(right_img, (left_img.width, 0))
        
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        
    return times


def benchmark_opencv_method(img_new, img_old, iterations=5):
    """Benchmark phương pháp OpenCV tối ưu"""
    if not OPTIMIZED_AVAILABLE:
        return None
    
    times = []
    
    for i in range(iterations):
        start = time.perf_counter()
        
        left_img, right_img = compare_images_opencv(
            img_new, img_old,
            diff_threshold=40,
            dilate_size=3,
            dilate_iterations=2,
            highlight_color="#ff0000",
            fill_opacity=40
        )
        side_by_side = create_side_by_side(left_img, right_img)
        
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return times


def benchmark_quick_hash(img_new, img_old, iterations=20):
    """Benchmark quick hash comparison"""
    if not OPTIMIZED_AVAILABLE:
        return None
    
    times = []
    
    for i in range(iterations):
        start = time.perf_counter()
        result = quick_compare_hash(img_new, img_old)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return times, result


def main():
    print("\n" + "="*60)
    print("BENCHMARK: PIL vs OpenCV Image Comparison")
    print("="*60)
    
    # Create test images
    print("\nCreating test images (2000x2800 pixels, ~A4 @ 100 DPI)...")
    img_old, img_new = create_test_images(width=2000, height=2800, diff_percent=5)
    print(f"   Image size: {img_old.size}")
    
    # Test 1: Quick Hash
    print("\n" + "-"*60)
    print("Test 1: Quick Hash Comparison (Short-circuit check)")
    print("-"*60)
    
    if OPTIMIZED_AVAILABLE:
        hash_times, is_identical = benchmark_quick_hash(img_new, img_old, iterations=20)
        avg_hash = sum(hash_times) / len(hash_times) * 1000  # ms
        print(f"   Average time: {avg_hash:.3f} ms")
        print(f"   Images identical: {is_identical}")
        print(f"   -> Neu anh giong nhau, bo qua toan bo xu ly nang!")
    else:
        print("   [!] Optimized module not available")
    
    # Test 2: PIL Method
    print("\n" + "-"*60)
    print("Test 2: PIL Method (Legacy)")
    print("-"*60)
    
    pil_times = benchmark_pil_method(img_new, img_old, iterations=5)
    avg_pil = sum(pil_times) / len(pil_times)
    print(f"   Times: {[f'{t:.3f}s' for t in pil_times]}")
    print(f"   Average: {avg_pil:.3f} seconds")
    
    # Test 3: OpenCV Method
    print("\n" + "-"*60)
    print("Test 3: OpenCV Method (Optimized)")
    print("-"*60)
    
    if OPTIMIZED_AVAILABLE:
        opencv_times = benchmark_opencv_method(img_new, img_old, iterations=5)
        if opencv_times:
            avg_opencv = sum(opencv_times) / len(opencv_times)
            print(f"   Times: {[f'{t:.3f}s' for t in opencv_times]}")
            print(f"   Average: {avg_opencv:.3f} seconds")
            
            # Calculate speedup
            speedup = avg_pil / avg_opencv
            improvement = (1 - avg_opencv / avg_pil) * 100
            
            print("\n" + "="*60)
            print("RESULTS SUMMARY")
            print("="*60)
            print(f"   PIL Average:     {avg_pil:.3f} seconds")
            print(f"   OpenCV Average:  {avg_opencv:.3f} seconds")
            print(f"   [SPEEDUP]        {speedup:.1f}x faster")
            print(f"   [IMPROVEMENT]    {improvement:.1f}% reduction in time")
            print("="*60)
    else:
        print("   [!] OpenCV not available, cannot benchmark")
    
    print("\n[DONE] Benchmark completed!")


if __name__ == "__main__":
    main()

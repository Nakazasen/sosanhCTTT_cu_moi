from PIL import Image, ImageChops, ImageDraw, ImageFilter
import numpy as np
import os
import utils
import config

class ImageComparisonService:
    @staticmethod
    def hex_to_rgba(hex_color, opacity=100):
        """Chuyển mã màu hex và độ mờ thành tuple RGBA"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        alpha = int(255 * opacity / 100)
        return (r, g, b, alpha)
    
    @staticmethod
    def compare_images(img1_path, img2_path, output_path, 
                       diff_threshold=40, 
                       highlight_color="#ff0000",
                       fill_opacity=40,
                       dilate_size=3,
                       dilate_iterations=2):
        """
        Compares two images and saves the difference image with highlights.
        
        Args:
            img1_path: Path to first (new) image
            img2_path: Path to second (old) image
            output_path: Path to save difference image
            diff_threshold: Pixel difference threshold (0-255)
            highlight_color: Hex color for highlighting differences
            fill_opacity: Opacity of highlight fill (0-100%)
            dilate_size: Size of dilation kernel (1-9, odd numbers)
            dilate_iterations: Number of dilation iterations (1-3)
        
        Returns: (has_differences, diff_score)
        """
        try:
            img1 = Image.open(img1_path).convert('RGB')
            img2 = Image.open(img2_path).convert('RGB')

            # Ensure same size
            if img1.size != img2.size:
                img2 = img2.resize(img1.size, Image.LANCZOS)

            # Compute difference
            diff = ImageChops.difference(img1, img2)
            
            # Check if difference is significant using threshold
            diff_array = np.array(diff)
            diff_mask = np.any(diff_array > diff_threshold, axis=2)
            diff_pixels = np.sum(diff_mask)
            
            if diff_pixels == 0:
                return False, 0
            
            # Calculate difference score
            total_pixels = diff_mask.size
            diff_score = int((diff_pixels / total_pixels) * 100)
            
            # Create highlight overlay
            # Dilate the difference mask to make highlights more visible
            from PIL import ImageFilter
            
            # Convert mask to image for dilation
            mask_img = Image.fromarray((diff_mask * 255).astype(np.uint8))
            
            # Apply dilation using MaxFilter (simulates morphological dilation)
            for _ in range(dilate_iterations):
                mask_img = mask_img.filter(ImageFilter.MaxFilter(dilate_size))
            
            # Create highlight overlay
            rgba_color = ImageComparisonService.hex_to_rgba(highlight_color, fill_opacity)
            highlight_overlay = Image.new('RGBA', img1.size, (0, 0, 0, 0))
            
            # Apply highlight color to difference areas
            highlight_data = np.array(highlight_overlay)
            dilated_mask = np.array(mask_img) > 0
            
            highlight_data[dilated_mask] = rgba_color
            highlight_overlay = Image.fromarray(highlight_data)
            
            # Composite onto original image (new image as base)
            result = img1.convert('RGBA')
            result = Image.alpha_composite(result, highlight_overlay)
            
            # Draw outline rectangles around difference regions
            draw = ImageDraw.Draw(result)
            outline_color = ImageComparisonService.hex_to_rgba(highlight_color, 100)[:3]
            
            # Find connected components (bounding boxes)
            bbox = mask_img.getbbox()
            if bbox:
                draw.rectangle(bbox, outline=outline_color, width=2)
            
            # Save result
            result.convert('RGB').save(output_path)
            utils.logger.info(f"Comparison complete: {diff_pixels} different pixels ({diff_score}%)")
            
            return True, diff_score
            
        except Exception as e:
            utils.logger.error(f"Image comparison failed: {e}")
            # Fallback: simple difference
            try:
                img1 = Image.open(img1_path)
                img2 = Image.open(img2_path)
                if img1.size != img2.size:
                    img2 = img2.resize(img1.size, Image.LANCZOS)
                diff = ImageChops.difference(img1.convert('RGB'), img2.convert('RGB'))
                if diff.getbbox():
                    diff.save(output_path)
                    return True, 100
            except:
                pass
            return False, 0

    @staticmethod
    def highlight_differences(diff_image_path, output_path, highlight_color="#ff0000", fill_opacity=40):
        """
        Post-processes the difference image to add red highlights.
        """
        try:
            diff_img = Image.open(diff_image_path).convert('RGBA')
            rgba_color = ImageComparisonService.hex_to_rgba(highlight_color, fill_opacity)
            
            # Find non-black pixels and highlight them
            diff_array = np.array(diff_img)
            non_zero_mask = np.any(diff_array[:,:,:3] > 10, axis=2)
            
            overlay = Image.new('RGBA', diff_img.size, (0, 0, 0, 0))
            overlay_data = np.array(overlay)
            overlay_data[non_zero_mask] = rgba_color
            overlay = Image.fromarray(overlay_data)
            
            result = Image.alpha_composite(diff_img, overlay)
            result.convert('RGB').save(output_path)
            
        except Exception as e:
            utils.logger.error(f"Highlight differences failed: {e}")

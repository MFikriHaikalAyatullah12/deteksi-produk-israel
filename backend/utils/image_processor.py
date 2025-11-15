import cv2
import numpy as np
from PIL import Image
import io
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.target_size = (640, 480)
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
    async def process_image(self, image_data: bytes) -> np.ndarray:
        """
        Process uploaded image data into a format suitable for analysis
        """
        try:
            # Check file size
            if len(image_data) > self.max_file_size:
                raise ValueError("File size too large. Maximum 10MB allowed.")
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            # Resize image
            processed_image = self._resize_image(image_bgr)
            
            # Apply preprocessing
            processed_image = self._preprocess_image(processed_image)
            
            return processed_image
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            raise ValueError(f"Cannot process image: {str(e)}")
    
    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """Resize image while maintaining aspect ratio"""
        height, width = image.shape[:2]
        target_width, target_height = self.target_size
        
        # Calculate scaling factor
        scale = min(target_width / width, target_height / height)
        
        # Calculate new dimensions
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # Create a black canvas and center the resized image
        canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        
        # Calculate position to center the image
        y_offset = (target_height - new_height) // 2
        x_offset = (target_width - new_width) // 2
        
        # Place the resized image on the canvas
        canvas[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = resized
        
        return canvas
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Apply preprocessing to improve detection accuracy"""
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        
        # Enhance contrast using CLAHE
        lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Sharpen the image
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return sharpened
    
    def extract_regions(self, image: np.ndarray) -> dict:
        """Extract different regions of interest from the image"""
        height, width = image.shape[:2]
        
        regions = {
            'full': image,
            'top': image[:height//3, :],
            'middle': image[height//3:2*height//3, :],
            'bottom': image[2*height//3:, :],
            'left': image[:, :width//2],
            'right': image[:, width//2:],
            'center': image[height//4:3*height//4, width//4:3*width//4]
        }
        
        return regions
    
    def detect_text_regions(self, image: np.ndarray) -> list:
        """Detect potential text regions in the image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply MSER (Maximally Stable Extremal Regions) for text detection
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)
        
        # Convert regions to bounding boxes
        bounding_boxes = []
        for region in regions:
            if len(region) > 10:  # Filter out too small regions
                x, y, w, h = cv2.boundingRect(region)
                # Filter by aspect ratio and size
                aspect_ratio = w / h if h > 0 else 0
                if 0.1 < aspect_ratio < 10 and w > 10 and h > 5:
                    bounding_boxes.append((x, y, w, h))
        
        return bounding_boxes
    
    def enhance_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Enhance image specifically for OCR"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply morphological operations to clean up text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological closing to connect text components
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Invert if text is white on dark background
        if np.mean(closed) > 127:
            closed = cv2.bitwise_not(closed)
        
        return closed
    
    def detect_barcodes_regions(self, image: np.ndarray) -> list:
        """Detect potential barcode regions"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Sobel operator to detect vertical edges (common in barcodes)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_x = np.abs(sobel_x)
        sobel_x = sobel_x.astype(np.uint8)
        
        # Apply morphological operations to connect barcode lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 1))
        closed = cv2.morphologyEx(sobel_x, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by aspect ratio and size
        barcode_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Barcodes typically have high aspect ratio (wider than tall)
            if aspect_ratio > 2 and w > 50 and h > 10:
                barcode_regions.append((x, y, w, h))
        
        return barcode_regions
    
    def extract_color_features(self, image: np.ndarray) -> dict:
        """Extract color-based features from the image"""
        # Convert to different color spaces
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Calculate histograms
        hist_h = cv2.calcHist([hsv], [0], None, [50], [0, 180])
        hist_s = cv2.calcHist([hsv], [1], None, [50], [0, 256])
        hist_v = cv2.calcHist([hsv], [2], None, [50], [0, 256])
        
        # Normalize histograms
        hist_h = hist_h.flatten() / hist_h.sum()
        hist_s = hist_s.flatten() / hist_s.sum()
        hist_v = hist_v.flatten() / hist_v.sum()
        
        # Calculate dominant colors
        dominant_colors = self._get_dominant_colors(image)
        
        return {
            'hue_histogram': hist_h,
            'saturation_histogram': hist_s,
            'value_histogram': hist_v,
            'dominant_colors': dominant_colors,
            'brightness': np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)),
            'contrast': np.std(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        }
    
    def _get_dominant_colors(self, image: np.ndarray, k: int = 5) -> list:
        """Get dominant colors using K-means clustering"""
        # Reshape image to be a list of pixels
        pixels = image.reshape(-1, 3)
        pixels = np.float32(pixels)
        
        # Apply K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert centers to integers
        centers = np.uint8(centers)
        
        # Count the frequency of each cluster
        unique, counts = np.unique(labels, return_counts=True)
        
        # Sort by frequency
        sorted_indices = np.argsort(-counts)
        dominant_colors = centers[sorted_indices].tolist()
        
        return dominant_colors[:3]  # Return top 3 dominant colors
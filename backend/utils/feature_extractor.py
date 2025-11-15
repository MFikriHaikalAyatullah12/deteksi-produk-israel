import cv2
import numpy as np
import easyocr
from pyzbar import pyzbar
import re
import logging
from typing import Dict, List, Any, Tuple, Optional
import asyncio

logger = logging.getLogger(__name__)

class FeatureExtractor:
    def __init__(self):
        # Initialize EasyOCR reader for multiple languages
        self.ocr_reader = easyocr.Reader(['en', 'ar', 'he'], gpu=False)
        
        # Israeli brand keywords and patterns
        self.israeli_brands = {
            # Unilever products
            'dove', 'rexona', 'lux', 'vaseline', 'ponds', 'lifebuoy', 'clear',
            'sunsilk', 'tresemme', 'rinso', 'molto', 'sunlight', 'pepsodent',
            'close up', 'blue band', 'royco', 'bango', 'sariwangi',
            
            # Nestlé products
            'nescafe', 'milo', 'kitkat', 'maggi', 'dancow', 'nestum',
            'pure life', 'carnation',
            
            # P&G products
            'pampers', 'pantene', 'head shoulders', 'rejoice', 'oral-b',
            'gillette', 'always', 'downy', 'ambi pur',
            
            # Coca-Cola products
            'coca cola', 'sprite', 'fanta', 'minute maid', 'aquarius', 'ades',
            
            # PepsiCo products
            'pepsi', 'lays', 'cheetos', 'quaker', 'gatorade', 'tropicana',
            
            # L'Oréal products
            'loreal', 'garnier', 'maybelline', 'nyx', 'vichy', 'la roche-posay',
            
            # Estée Lauder products
            'estee lauder', 'mac', 'clinique', 'bobbi brown', 'origins', 'aveda',
            
            # Others
            'mcdonalds', 'starbucks', 'heinz', 'kraft', 'sabon'
        }
        
        # Hebrew text patterns (common Hebrew words on products)
        self.hebrew_patterns = [
            r'[\u0590-\u05FF]+',  # Hebrew Unicode range
        ]
        
        # "Made in Israel" text patterns in multiple languages
        self.made_in_israel_patterns = [
            r'made\s+in\s+israel',
            r'product\s+of\s+israel',
            r'manufactured\s+in\s+israel',
            r'produced\s+in\s+israel',
            r'israel',
            r'israeli\s+product'
        ]
        
        # Kosher certification patterns
        self.kosher_patterns = [
            r'kosher',
            r'halal',
            r'badatz',
            r'ou\s*kosher',
            r'kof-k',
            r'star-k',
            r'ok\s*kosher',
            r'kashrus',
            r'pareve',
            r'dairy',
            r'meat',
            r'ⓤ',  # OU symbol
            r'ⓚ',  # K symbol
        ]
        
    async def extract_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract all features from the processed image"""
        try:
            features = {}
            
            # Extract barcode information
            barcode_info = await self._extract_barcode_features(image)
            features.update(barcode_info)
            
            # Extract text features
            text_info = await self._extract_text_features(image)
            features.update(text_info)
            
            # Extract brand information
            brand_info = await self._extract_brand_features(image, text_info.get('detected_text', ''))
            features.update(brand_info)
            
            # Extract visual features
            visual_info = await self._extract_visual_features(image)
            features.update(visual_info)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return self._get_default_features()
    
    async def _extract_barcode_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract barcode-related features"""
        features = {
            'barcode_729': False,
            'barcode_detected': False,
            'barcode_confidence': 0.0
        }
        
        try:
            # Convert to grayscale for better barcode detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect barcodes
            barcodes = pyzbar.decode(gray)
            
            if barcodes:
                features['barcode_detected'] = True
                features['barcode_confidence'] = 0.9
                
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    logger.info(f"Detected barcode: {barcode_data}")
                    
                    # Check for Israeli barcode prefix (729)
                    if barcode_data.startswith('729'):
                        features['barcode_729'] = True
                        features['barcode_confidence'] = 1.0
                        break
            
            # If no barcode detected, try alternative methods
            if not features['barcode_detected']:
                # Look for barcode-like patterns in text
                text_result = self.ocr_reader.readtext(gray)
                for detection in text_result:
                    text = detection[1].replace(' ', '').replace('-', '')
                    if len(text) >= 8 and text.isdigit():
                        if text.startswith('729'):
                            features['barcode_729'] = True
                            features['barcode_detected'] = True
                            features['barcode_confidence'] = 0.7
                            break
                            
        except Exception as e:
            logger.warning(f"Error in barcode detection: {str(e)}")
        
        return features
    
    async def _extract_text_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text-related features"""
        features = {
            'made_in_israel_text': False,
            'hebrew_text': False,
            'kosher_certification': False,
            'text_confidence': 0.0,
            'detected_text': ''
        }
        
        try:
            # Use EasyOCR to extract text
            results = self.ocr_reader.readtext(image)
            
            all_text = []
            total_confidence = 0
            
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Only consider high-confidence detections
                    all_text.append(text.lower())
                    total_confidence += confidence
            
            if all_text:
                features['text_confidence'] = total_confidence / len(results)
                full_text = ' '.join(all_text)
                features['detected_text'] = full_text
                
                # Check for "Made in Israel" patterns
                for pattern in self.made_in_israel_patterns:
                    if re.search(pattern, full_text, re.IGNORECASE):
                        features['made_in_israel_text'] = True
                        break
                
                # Check for Hebrew text
                for pattern in self.hebrew_patterns:
                    if re.search(pattern, full_text):
                        features['hebrew_text'] = True
                        break
                
                # Check for kosher certification
                for pattern in self.kosher_patterns:
                    if re.search(pattern, full_text, re.IGNORECASE):
                        features['kosher_certification'] = True
                        break
                        
        except Exception as e:
            logger.warning(f"Error in text extraction: {str(e)}")
        
        return features
    
    async def _extract_brand_features(self, image: np.ndarray, detected_text: str) -> Dict[str, Any]:
        """Extract brand-related features"""
        features = {
            'israeli_brand': False,
            'brand_confidence': 0.0,
            'detected_brand': None
        }
        
        try:
            text_lower = detected_text.lower()
            
            # Check for known Israeli-affiliated brands
            for brand in self.israeli_brands:
                # Check exact match
                if brand in text_lower:
                    features['israeli_brand'] = True
                    features['brand_confidence'] = 0.9
                    features['detected_brand'] = brand
                    break
                
                # Check partial match (for multi-word brands)
                brand_words = brand.split()
                if len(brand_words) > 1:
                    if all(word in text_lower for word in brand_words):
                        features['israeli_brand'] = True
                        features['brand_confidence'] = 0.8
                        features['detected_brand'] = brand
                        break
            
            # Additional logo-based detection could be implemented here
            # using image classification or template matching
            
        except Exception as e:
            logger.warning(f"Error in brand detection: {str(e)}")
        
        return features
    
    async def _extract_visual_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract visual features from the image"""
        features = {
            'logo_confidence': 0.0,
            'package_analysis': 0.0,
            'color_analysis': 0.0
        }
        
        try:
            # Analyze image composition and quality
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate image sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate contrast
            contrast = gray.std()
            
            # Analyze color distribution
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1, 2], None, [50, 60, 60], [0, 180, 0, 256, 0, 256])
            color_diversity = np.count_nonzero(hist) / hist.size
            
            # Detect potential logo regions
            logo_score = self._detect_logo_regions(image)
            
            # Package analysis (based on text density and layout)
            package_score = self._analyze_package_layout(image)
            
            # Normalize scores
            features['logo_confidence'] = min(logo_score, 1.0)
            features['package_analysis'] = min(package_score, 1.0)
            features['color_analysis'] = min(color_diversity * 2, 1.0)  # Multiply by 2 to scale
            
        except Exception as e:
            logger.warning(f"Error in visual feature extraction: {str(e)}")
        
        return features
    
    def _detect_logo_regions(self, image: np.ndarray) -> float:
        """Detect potential logo regions in the image"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            logo_score = 0.0
            for contour in contours:
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                
                if perimeter > 0:
                    # Calculate circularity (logos often have circular/rectangular shapes)
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    
                    # Check if area is reasonable for a logo
                    if 500 < area < 5000 and 0.3 < circularity < 1.2:
                        logo_score += 0.1
            
            return min(logo_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Error in logo detection: {str(e)}")
            return 0.0
    
    def _analyze_package_layout(self, image: np.ndarray) -> float:
        """Analyze the package layout and structure"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find text regions using morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
            text_regions = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            # Count text regions
            contours, _ = cv2.findContours(text_regions, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            text_count = len(contours)
            
            # Analyze layout structure
            # Products typically have structured layout with text in specific regions
            package_score = min(text_count / 20.0, 1.0)  # Normalize based on expected text regions
            
            return package_score
            
        except Exception as e:
            logger.warning(f"Error in package analysis: {str(e)}")
            return 0.0
    
    def _get_default_features(self) -> Dict[str, Any]:
        """Return default feature set when extraction fails"""
        return {
            'barcode_729': False,
            'made_in_israel_text': False,
            'hebrew_text': False,
            'israeli_brand': False,
            'kosher_certification': False,
            'brand_confidence': 0.0,
            'text_confidence': 0.0,
            'logo_confidence': 0.0,
            'package_analysis': 0.0,
            'color_analysis': 0.0,
            'detected_text': '',
            'detected_brand': None,
            'barcode_detected': False,
            'barcode_confidence': 0.0
        }
    
    async def extract_batch_features(self, images: List[np.ndarray]) -> List[Dict[str, Any]]:
        """Extract features from multiple images"""
        tasks = [self.extract_features(image) for image in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in batch processing: {str(result)}")
                processed_results.append(self._get_default_features())
            else:
                processed_results.append(result)
        
        return processed_results
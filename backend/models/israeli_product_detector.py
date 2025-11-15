import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio

logger = logging.getLogger(__name__)

class IsraeliProductDetector:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.brands_database = None
        self.is_initialized = False
        
        # Feature mapping for easier interpretation
        self.feature_map = {
            0: "barcode_729",
            1: "made_in_israel_text", 
            2: "hebrew_text",
            3: "israeli_brand",
            4: "kosher_certification",
            5: "brand_confidence",
            6: "text_confidence",
            7: "logo_confidence",
            8: "package_analysis",
            9: "color_analysis"
        }
        
        # Load brands database
        self._load_brands_database()
    
    def _load_brands_database(self):
        """Load database of Israeli-affiliated brands"""
        self.brands_database = {
            "unilever": {
                "products": [
                    "dove", "rexona", "lux", "vaseline", "ponds", "lifebuoy", 
                    "clear", "sunsilk", "tresemme", "rinso", "molto", "sunlight",
                    "pepsodent", "close up", "blue band", "royco", "bango", "sariwangi"
                ],
                "category": "consumer_goods",
                "risk_level": "high"
            },
            "nestle": {
                "products": [
                    "nescafe", "milo", "kitkat", "maggi", "dancow", "nestum",
                    "pure life", "carnation", "smarties", "aero", "crunch"
                ],
                "category": "food_beverage", 
                "risk_level": "high"
            },
            "procter_gamble": {
                "products": [
                    "pampers", "pantene", "head shoulders", "rejoice", "oral-b",
                    "gillette", "always", "downy", "ambi pur", "tide", "ariel"
                ],
                "category": "personal_care",
                "risk_level": "high"
            },
            "coca_cola": {
                "products": [
                    "coca cola", "sprite", "fanta", "minute maid", "aquarius", "ades"
                ],
                "category": "beverages",
                "risk_level": "high"
            },
            "pepsico": {
                "products": [
                    "pepsi", "lays", "cheetos", "quaker", "gatorade", "tropicana"
                ],
                "category": "food_beverage",
                "risk_level": "high"
            },
            "loreal": {
                "products": [
                    "l'oreal paris", "garnier", "maybelline", "nyx", "vichy", 
                    "la roche-posay", "kerastase", "matrix"
                ],
                "category": "cosmetics",
                "risk_level": "high"
            },
            "estee_lauder": {
                "products": [
                    "estee lauder", "mac", "clinique", "bobbi brown", 
                    "origins", "aveda", "too faced"
                ],
                "category": "cosmetics",
                "risk_level": "high"
            },
            "kraft_heinz": {
                "products": [
                    "heinz", "kraft", "abc", "salsa"
                ],
                "category": "food",
                "risk_level": "medium"
            },
            "mcdonalds": {
                "products": ["mcdonalds", "mcd"],
                "category": "fast_food",
                "risk_level": "high"
            },
            "starbucks": {
                "products": ["starbucks"],
                "category": "beverages",
                "risk_level": "medium"
            }
        }
        
    async def initialize(self):
        """Initialize the model with training data"""
        try:
            # Generate synthetic training data
            training_data = self._generate_training_data()
            
            # Prepare features and labels
            X = training_data.drop(['label', 'brand_name'], axis=1)
            y = training_data['label']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Model trained successfully with accuracy: {accuracy:.3f}")
            
            # Store feature names
            self.feature_names = X.columns.tolist()
            self.is_initialized = True
            
            # Save model (optional)
            self._save_model()
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            raise
    
    def _generate_training_data(self) -> pd.DataFrame:
        """Generate synthetic training data for Israeli product detection"""
        data = []
        
        # Generate positive samples (Israeli products)
        for brand, info in self.brands_database.items():
            for product in info["products"]:
                # High confidence Israeli products
                for _ in range(20):
                    sample = {
                        'barcode_729': np.random.choice([0, 1], p=[0.3, 0.7]),
                        'made_in_israel_text': np.random.choice([0, 1], p=[0.4, 0.6]),
                        'hebrew_text': np.random.choice([0, 1], p=[0.6, 0.4]),
                        'israeli_brand': 1,
                        'kosher_certification': np.random.choice([0, 1], p=[0.3, 0.7]),
                        'brand_confidence': np.random.uniform(0.7, 1.0),
                        'text_confidence': np.random.uniform(0.6, 0.9),
                        'logo_confidence': np.random.uniform(0.8, 1.0),
                        'package_analysis': np.random.uniform(0.6, 0.9),
                        'color_analysis': np.random.uniform(0.5, 0.8),
                        'label': 1,
                        'brand_name': brand
                    }
                    data.append(sample)
        
        # Generate negative samples (non-Israeli products)
        local_brands = [
            'indofood', 'wings', 'mayora', 'garuda', 'abc', 'teh botol',
            'aqua', 'indomie', 'chitato', 'tolak angin', 'kopi kapal api',
            'ultra milk', 'dancow', 'good day', 'silverqueen', 'top coffee'
        ]
        
        for brand in local_brands:
            for _ in range(25):
                sample = {
                    'barcode_729': 0,  # No Israeli barcode
                    'made_in_israel_text': 0,  # No "Made in Israel" text
                    'hebrew_text': 0,  # No Hebrew text
                    'israeli_brand': 0,  # Not an Israeli brand
                    'kosher_certification': np.random.choice([0, 1], p=[0.9, 0.1]),
                    'brand_confidence': np.random.uniform(0.6, 0.9),
                    'text_confidence': np.random.uniform(0.5, 0.8),
                    'logo_confidence': np.random.uniform(0.7, 0.95),
                    'package_analysis': np.random.uniform(0.5, 0.8),
                    'color_analysis': np.random.uniform(0.4, 0.7),
                    'label': 0,
                    'brand_name': brand
                }
                data.append(sample)
        
        # Add some ambiguous cases
        for _ in range(100):
            sample = {
                'barcode_729': np.random.choice([0, 1], p=[0.8, 0.2]),
                'made_in_israel_text': np.random.choice([0, 1], p=[0.9, 0.1]),
                'hebrew_text': np.random.choice([0, 1], p=[0.9, 0.1]),
                'israeli_brand': np.random.choice([0, 1], p=[0.7, 0.3]),
                'kosher_certification': np.random.choice([0, 1], p=[0.6, 0.4]),
                'brand_confidence': np.random.uniform(0.3, 0.7),
                'text_confidence': np.random.uniform(0.3, 0.6),
                'logo_confidence': np.random.uniform(0.4, 0.7),
                'package_analysis': np.random.uniform(0.3, 0.7),
                'color_analysis': np.random.uniform(0.3, 0.6),
                'label': np.random.choice([0, 1], p=[0.6, 0.4]),
                'brand_name': 'unknown'
            }
            data.append(sample)
        
        return pd.DataFrame(data)
    
    async def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction on extracted features"""
        if not self.is_initialized:
            raise ValueError("Model not initialized")
        
        start_time = datetime.now()
        
        try:
            # Convert features to numpy array
            feature_vector = self._features_to_vector(features)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            # Make prediction
            prediction = self.model.predict(feature_vector_scaled)[0]
            probability = self.model.predict_proba(feature_vector_scaled)[0]
            
            # Get confidence score
            confidence = max(probability)
            
            # Analyze detected features
            detected_features = {
                "barcode_729": features.get("barcode_729", False),
                "made_in_israel_text": features.get("made_in_israel_text", False),
                "hebrew_text": features.get("hebrew_text", False),
                "israeli_brand": features.get("israeli_brand", False),
                "kosher_certification": features.get("kosher_certification", False)
            }
            
            # Get brand information if detected
            brand_info = None
            if features.get("detected_brand"):
                brand_info = self._get_brand_info(features["detected_brand"])
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "is_israeli_product": bool(prediction),
                "confidence": float(confidence),
                "features": detected_features,
                "brand_info": brand_info,
                "processing_time_ms": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise
    
    def _features_to_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """Convert feature dictionary to numpy array"""
        vector = []
        for feature_name in self.feature_names:
            if feature_name in features:
                value = features[feature_name]
                if isinstance(value, bool):
                    vector.append(1.0 if value else 0.0)
                else:
                    vector.append(float(value))
            else:
                vector.append(0.0)
        
        return np.array(vector)
    
    def _get_brand_info(self, brand_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a detected brand"""
        brand_lower = brand_name.lower()
        
        for brand_key, brand_data in self.brands_database.items():
            if brand_lower in [p.lower() for p in brand_data["products"]] or brand_lower == brand_key:
                return {
                    "name": brand_name,
                    "category": brand_data["category"],
                    "risk_level": brand_data["risk_level"]
                }
        
        return None
    
    def _save_model(self):
        """Save trained model and scaler"""
        try:
            joblib.dump(self.model, 'models/israeli_detector_model.pkl')
            joblib.dump(self.scaler, 'models/israeli_detector_scaler.pkl')
            
            with open('models/feature_names.json', 'w') as f:
                json.dump(self.feature_names, f)
            
            logger.info("Model saved successfully")
        except Exception as e:
            logger.warning(f"Could not save model: {str(e)}")
    
    def is_ready(self) -> bool:
        """Check if model is ready for predictions"""
        return self.is_initialized and self.model is not None
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        if not self.is_ready():
            return {"status": "not_ready"}
        
        return {
            "status": "ready",
            "model_type": "RandomForestClassifier",
            "n_estimators": self.model.n_estimators,
            "max_depth": self.model.max_depth,
            "feature_count": len(self.feature_names),
            "feature_names": self.feature_names,
            "brands_count": len(self.brands_database)
        }
    
    async def get_brands_database(self) -> Dict[str, Any]:
        """Get the brands database"""
        return self.brands_database
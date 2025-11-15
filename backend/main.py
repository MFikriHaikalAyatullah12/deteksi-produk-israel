import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from datetime import datetime
import logging

from models.israeli_product_detector import IsraeliProductDetector
from utils.image_processor import ImageProcessor
from utils.feature_extractor import FeatureExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Israeli Product Detection API",
    description="API untuk deteksi produk terafiliasi Israel menggunakan Random Forest",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
detector = IsraeliProductDetector()
image_processor = ImageProcessor()
feature_extractor = FeatureExtractor()

@app.on_event("startup")
async def startup_event():
    """Initialize the model and load training data"""
    try:
        logger.info("Loading Israeli product detection model...")
        await detector.initialize()
        logger.info("Model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Israeli Product Detection API",
        "status": "active",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_ready": detector.is_ready(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze")
async def analyze_product(image: UploadFile = File(...)):
    """
    Analyze uploaded image to detect Israeli-affiliated products
    """
    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File harus berupa gambar")
        
        # Read and process image
        image_data = await image.read()
        
        # Process image
        processed_image = await image_processor.process_image(image_data)
        
        # Extract features
        features = await feature_extractor.extract_features(processed_image)
        
        # Make prediction
        prediction_result = await detector.predict(features)
        
        # Prepare response
        result = {
            "is_israeli_product": prediction_result["is_israeli_product"],
            "confidence": prediction_result["confidence"],
            "detected_features": prediction_result["features"],
            "brand_info": prediction_result.get("brand_info"),
            "timestamp": datetime.now().isoformat(),
            "processing_time_ms": prediction_result.get("processing_time_ms", 0)
        }
        
        logger.info(f"Detection completed: {result['is_israeli_product']} (confidence: {result['confidence']:.3f})")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Terjadi kesalahan saat menganalisis gambar: {str(e)}"
        )

@app.post("/analyze/batch")
async def analyze_batch(images: list[UploadFile] = File(...)):
    """
    Analyze multiple images in batch
    """
    try:
        if len(images) > 10:
            raise HTTPException(status_code=400, detail="Maksimal 10 gambar per batch")
        
        results = []
        for idx, image in enumerate(images):
            try:
                # Validate file type
                if not image.content_type or not image.content_type.startswith('image/'):
                    results.append({
                        "index": idx,
                        "error": "File bukan gambar",
                        "filename": image.filename
                    })
                    continue
                
                # Process image
                image_data = await image.read()
                processed_image = await image_processor.process_image(image_data)
                
                # Extract features and predict
                features = await feature_extractor.extract_features(processed_image)
                prediction_result = await detector.predict(features)
                
                results.append({
                    "index": idx,
                    "filename": image.filename,
                    "is_israeli_product": prediction_result["is_israeli_product"],
                    "confidence": prediction_result["confidence"],
                    "detected_features": prediction_result["features"],
                    "brand_info": prediction_result.get("brand_info"),
                })
                
            except Exception as e:
                logger.error(f"Error processing image {idx} ({image.filename}): {str(e)}")
                results.append({
                    "index": idx,
                    "filename": image.filename,
                    "error": str(e)
                })
        
        return JSONResponse(content={
            "results": results,
            "total_processed": len(results),
            "timestamp": datetime.now().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during batch analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan saat menganalisis gambar: {str(e)}"
        )

@app.get("/model/info")
async def get_model_info():
    """Get information about the loaded model"""
    try:
        info = await detector.get_model_info()
        return JSONResponse(content=info)
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/brands/database")
async def get_brands_database():
    """Get the brands database"""
    try:
        brands = await detector.get_brands_database()
        return JSONResponse(content=brands)
    except Exception as e:
        logger.error(f"Error getting brands database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
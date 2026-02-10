from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoGrader OCR Service",
    description="Handwriting recognition service using TrOCR and EasyOCR",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class OCRResponse(BaseModel):
    text: str
    confidence: float
    model_used: str
    processing_time: float

class BatchOCRResponse(BaseModel):
    results: List[OCRResponse]
    total_processing_time: float

@app.get("/")
async def root():
    return {
        "service": "AutoGrader OCR Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/ocr/extract", response_model=OCRResponse)
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from a handwritten image using OCR.
    
    Args:
        file: Image file (jpg, png, pdf)
    
    Returns:
        OCRResponse with extracted text and confidence
    """
    try:
        # TODO: Implement actual OCR logic
        logger.info(f"Processing file: {file.filename}")
        
        # Placeholder response
        return OCRResponse(
            text="Sample extracted text - implementation pending",
            confidence=0.85,
            model_used="trocr-base-handwritten",
            processing_time=1.5
        )
    except Exception as e:
        logger.error(f"Error processing OCR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ocr/batch", response_model=BatchOCRResponse)
async def batch_extract_text(files: List[UploadFile] = File(...)):
    """
    Batch process multiple images for OCR.
    
    Args:
        files: List of image files
    
    Returns:
        BatchOCRResponse with results for all files
    """
    try:
        logger.info(f"Batch processing {len(files)} files")
        
        # TODO: Implement batch OCR logic
        results = [
            OCRResponse(
                text=f"Sample text from {file.filename}",
                confidence=0.85,
                model_used="trocr-base-handwritten",
                processing_time=1.5
            )
            for file in files
        ]
        
        return BatchOCRResponse(
            results=results,
            total_processing_time=len(files) * 1.5
        )
    except Exception as e:
        logger.error(f"Error in batch OCR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

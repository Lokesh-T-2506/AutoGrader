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

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
import time
import io

# Load TrOCR model and processor
logger.info("Loading TrOCR model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten").to(device)
logger.info(f"TrOCR model loaded on {device}")

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
        "version": "1.0.0",
        "device": device
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/ocr/extract", response_model=OCRResponse)
async def extract_text(file: UploadFile = File(...)):
    """
    Extract text from a handwritten image using TrOCR.
    """
    try:
        start_time = time.time()
        logger.info(f"Processing file: {file.filename}")
        
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Prepare image for model
        pixel_values = processor(image, return_tensors="pt").pixel_values.to(device)
        
        # Generate transcription
        generated_ids = model.generate(pixel_values)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        processing_time = time.time() - start_time
        logger.info(f"OCR completed in {processing_time:.2f}s")
        
        return OCRResponse(
            text=generated_text,
            confidence=0.90, # Placeholder confidence
            model_used="microsoft/trocr-base-handwritten",
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error processing OCR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ocr/batch", response_model=BatchOCRResponse)
async def batch_extract_text(files: List[UploadFile] = File(...)):
    """
    Batch process multiple images for OCR using TrOCR.
    """
    try:
        start_time = time.time()
        logger.info(f"Batch processing {len(files)} files")
        
        results = []
        for file in files:
            res = await extract_text(file)
            results.append(res)
        
        total_time = time.time() - start_time
        return BatchOCRResponse(
            results=results,
            total_processing_time=total_time
        )
    except Exception as e:
        logger.error(f"Error in batch OCR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

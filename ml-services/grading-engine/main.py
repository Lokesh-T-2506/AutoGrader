"""
AutoGrader Grading Engine  v4.0 (Vision-First)
Professional Multimodal AI Grading System.
Directly grades student handwriting crops using Gemini 2.0 Flash.
Removed: SymPy, Sentence-BERT, Torch (Eliminating deadlocks and overhead).
New: Multimodal Vision Grading + AI Concept Discovery.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
import logging
import os
import json
import re
import random
import asyncio
import httpx
from dotenv import load_dotenv

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

log_file = r"c:\Users\tallu\OneDrive\Desktop\AutoGrader\ml-services\grading-engine\grading_engine.log"
fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(fh)
logging.getLogger().addHandler(fh)
logging.getLogger().setLevel(logging.INFO)

# ── Config ────────────────────────────────────────────────────────────────────

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
api_key = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-2.5-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

if api_key:
    logger.info(f"GEMINI_API_KEY loaded ({api_key[:10]}...)")
else:
    logger.error("GEMINI_API_KEY not found — Vision Grading will fail!")

# Serialise Gemini calls to stay within free-tier quota
_gemini_sem = asyncio.Semaphore(1)

# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="AutoGrader Grading Engine",
    description="Vision-First Multimodal AI Grader",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Data models ───────────────────────────────────────────────────────────────

class GradeRequest(BaseModel):
    student_image_b64: str  # Base64 string of the handwriting crop
    reference_solution: str
    rubric_text: str
    question_text: str = ""

class CriterionScore(BaseModel):
    criterion_id: str
    points_awarded: float
    max_points: float
    confidence: float
    reasoning: str
    matched_concepts: List[str]

class GradeResponse(BaseModel):
    total_score: float
    max_score: float
    percentage: float
    requires_manual_review: bool = False
    criterion_scores: List[CriterionScore]
    overall_confidence: float
    discovered_concept: str = "Unknown"  # AI figured this out

class BatchZoneData(BaseModel):
    image_b64: str
    reference_text: Optional[str] = None
    reference_image_b64: Optional[str] = None
    max_score: float = 10.0

class BatchVisionRequest(BaseModel):
    zones: Dict[str, BatchZoneData]
    rubric: str = "Grade based on accuracy and units."
    student_id: str = "student_001"

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"service": "AutoGrader Grading Engine", "status": "running", "version": "4.1.0",
            "signals": ["Gemini 2.0 Flash Multimodal", "Visual Ground Truth"]}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ── Multimodal Library ────────────────────────────────────────────────────────

def build_multimodal_prompt(reference: str, rubric: str, question: str) -> str:
    q_section = f"\n### QUESTION CONTEXT:\n{question}\n" if question.strip() else ""
    return f"""You are an expert Teaching Assistant. Look at the attached image of a student's handwritten answer.
{q_section}
### INSTRUCTOR REFERENCE SOLUTION (Ground Truth):
{reference}

### RUBRIC:
{rubric}

### GRADING INSTRUCTIONS:
1. Allow mathematically equivalent variations.
2. A student who shows full working that arrives at the correct result earns full credit.
3. Transcribe what you see in the image and grade it.
4. If handwriting is illegible, lower confidence and flag for review.
5. Identify the core physics/math concept the student is using (e.g. 'Ohm's Law', 'Conservation of Energy').
6. Output ONLY valid JSON — no markdown.

{{
  "total_score": <float>,
  "max_score": <float>,
  "requires_manual_review": <boolean>,
  "overall_confidence": <float 0-1>,
  "discovered_concept": "<string — core concept name>",
  "criterion_scores": [
    {{
      "criterion_id": "<string>",
      "points_awarded": <float>,
      "max_points": <float>,
      "confidence": <float 0-1>,
      "reasoning": "<string — one sentence explanation>",
      "matched_concepts": ["<concept1>", ...]
    }}
  ]
}}"""

async def call_gemini_multimodal(image_b64: str, prompt: str, max_retries: int = 5) -> Optional[dict]:
    if not api_key:
        return None

    url = (
        f"{BASE_URL}/{MODEL_NAME}:generateContent?key={api_key}"
    )
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_b64
                    }
                }
            ]
        }],
        "generationConfig": {"temperature": 0.1},
    }

    # More aggressive delays for the demo to handle free-tier 429s
    base_delays = [30, 60, 120]

    # Semaphore removed for demo-day troubleshooting
    if True:
        await asyncio.sleep(1)
        
        async with httpx.AsyncClient(timeout=300) as client:
            for attempt in range(max_retries):
                try:
                    resp = await client.post(url, headers=headers, json=payload)

                    if resp.status_code != 200:
                        logger.error(f"Gemini API Error: {resp.status_code} - {resp.text}")
                        if resp.status_code == 429:
                            wait = base_delays[min(attempt, len(base_delays) - 1)]
                            logger.warning(f"Retrying in {wait}s...")
                            await asyncio.sleep(wait)
                            continue
                        # Return None immediately for other errors during diagnosis
                        return None

                    resp.raise_for_status()
                    data = resp.json()

                    candidates = data.get("candidates", [])
                    if not candidates:
                        return None

                    raw = candidates[0]["content"]["parts"][0]["text"].strip()
                    
                    # ── DEBUG LOGGING ──────────────────────────────────────────
                    logger.info("Raw Gemini Response received.")
                    with open("DEBUG_GEMINI_RESPONSE.json", "w", encoding="utf-8") as f:
                        f.write(raw)
                    logger.info(f"Raw response saved to DEBUG_GEMINI_RESPONSE.json for inspection.")
                    # ──────────────────────────────────────────────────────────

                    raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("` \n")
                    result = json.loads(raw)
                    return result

                except Exception as e:
                    logger.error(f"Gemini Vision call error (attempt {attempt+1}): {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(10)

    return None

# ── Main grading endpoint ─────────────────────────────────────────────────────

@app.post("/api/grade/vision", response_model=GradeResponse)
async def evaluate_vision_submission(request: GradeRequest):
    """
    Direct Vision-First Grading.
    AI sees the image, applies the rubric, and discovers the concept.
    """
    try:
        logger.info("=== Vision-First Grading Request ===")
        
        prompt = build_multimodal_prompt(
            request.reference_solution, 
            request.rubric_text, 
            request.question_text
        )
        
        result = await call_gemini_multimodal(request.student_image_b64, prompt)
        
        if result is None:
            raise HTTPException(status_code=503, detail="Gemini Grading Service Unavailable (Rate Limit or API Error)")

        total = result.get("total_score", 0.0)
        max_s = result.get("max_score", 1.0)
        pct   = round((total / max_s * 100), 2) if max_s > 0 else 0.0

        return GradeResponse(
            total_score            = total,
            max_score              = max_s,
            percentage             = pct,
            requires_manual_review = result.get("requires_manual_review", False),
            criterion_scores       = [
                CriterionScore(**cs) for cs in result.get("criterion_scores", [])
            ],
            overall_confidence     = result.get("overall_confidence", 0.0),
            discovered_concept     = result.get("discovered_concept", "Physics Application")
        )

    except Exception as e:
        logger.error(f"Error in evaluate_vision_submission: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/grade/batch-vision")
async def grade_batch_vision(request: BatchVisionRequest):
    """
    ONE GO (Visual Ground Truth Edition): 
    Evaluates all zones by comparing Student Image vs Instructor Key Image.
    """
    if not api_key:
        raise HTTPException(500, "GEMINI_API_KEY not found")

    parts = []
    
    # Primary Grading Context
    parts.append({
        "text": f"You are a professional instructor grading a physics/math exam for student {request.student_id}.\n"
                f"Global Rubric: {request.rubric}\n\n"
                "INSTRUCTIONS:\n"
                "1. For each zone, I will provide a Student Image and an Instructor Key Image.\n"
                "2. The Instructor Key Image is the ABSOLUTE GROUND TRUTH.\n"
                "3. Grade based on logical equivalence to the key. Award partial credit for correct steps.\n"
                "4. Return a JSON object mapping Zone IDs to results."
    })

    # Interleave each Image + Specific Reference
    for zone_id, data in request.zones.items():
        # First: THE STUDENT ANSWER
        parts.append({"text": f"--- ZONE: {zone_id} ---"})
        parts.append({"text": "STUDENT ANSWER IMAGE:"})
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": data.image_b64
            }
        })
        
        # Second: THE INSTRUCTOR KEY (Visual Ground Truth)
        if data.reference_image_b64:
            parts.append({"text": "INSTRUCTOR KEY IMAGE (Source of Truth):"})
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": data.reference_image_b64
                }
            })
        elif data.reference_text:
            parts.append({"text": f"INSTRUCTOR REFERENCE TEXT: {data.reference_text}"})

        parts.append({
            "text": f"Evaluate results for Zone '{zone_id}'. Max score: {data.max_score}."
        })

    # Final Formatting Push
    parts.append({
        "text": "\nFINAL INSTRUCTION: Respond ONLY in valid JSON. Format each zone result as:\n"
                "\"zone_id\": {\"score\": float, \"max_score\": float, \"confidence\": float, \"reasoning\": \"string\", \"concept\": \"string\"}"
    })

    url = f"{BASE_URL}/{MODEL_NAME}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.1,
            "response_mime_type": "application/json"
        }
    }

    async with _gemini_sem:
        async with httpx.AsyncClient(timeout=300) as client:
            for attempt in range(3):
                try:
                    resp = await client.post(url, headers=headers, json=payload)
                    
                    if resp.status_code == 429:
                        wait_time = [30, 60, 120][attempt]
                        logger.warning(f"Gemini 429 (Batch) - Quota limit reached. Retrying in {wait_time}s (Attempt {attempt+1}/3)...")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    if resp.status_code != 200:
                        logger.error(f"Gemini API Error: {resp.status_code} - {resp.text}")
                        raise HTTPException(500, f"Gemini API Error: {resp.status_code}")
                    
                    raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    # Clean markdown markers
                    raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("` \n")
                    
                    results = json.loads(raw)
                    # Inject metadata for analytics compatibility
                    final_output = []
                    for zid, res in results.items():
                        final_output.append({
                            "student_id": request.student_id,
                            "zone_id": zid,
                            "score": res.get("score", 0.0),
                            "max_score": res.get("max_score", 10.0),
                            "confidence": res.get("confidence", 0.0),
                            "reasoning": res.get("reasoning", "N/A"),
                            "concept": res.get("concept", "Physics")
                        })
                    return final_output

                except Exception as e:
                    if attempt == 2:
                        logger.error(f"Batch Vision final failure: {e}")
                        raise HTTPException(500, detail=str(e))
                    logger.warning(f"Batch Vision attempt {attempt+1} failed: {e}. Retrying...")
                    await asyncio.sleep(10)

# MLServiceClient.java snippet for reference:
# Map<String, Object> payload = Map.of(
#         "student_image_b64", imageB64,
#         "reference_image_b64", referenceImageB64 != null ? referenceImageB64 : "",
#         "reference_solution", "Instructor solution provided in image.",
#         "rubric_text", rubric,
#         "question_text", "Zone " + zoneId
# );

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging
import os
import json
import re
import httpx
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
if GEMINI_API_KEY:
    logger.info(f"GEMINI_API_KEY loaded ({GEMINI_API_KEY[:10]}...)")
else:
    logger.warning("GEMINI_API_KEY not found — feedback will return placeholders.")

app = FastAPI(
    title="AutoGrader Feedback Generator",
    description="Structured AI feedback generation for student submissions",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ?????? Data models ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

class FeedbackRequest(BaseModel):
    student_answer: str
    expected_answer: str
    score: float
    max_score: float
    rubric_description: str
    identified_errors: List[str] = []
    tone: Optional[str] = "constructive"  # constructive | encouraging | strict

class FeedbackResponse(BaseModel):
    feedback: str
    suggestions: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]
    tone: str

class ImproveFeedbackRequest(BaseModel):
    original_feedback: str
    tone_preference: Optional[str] = "constructive"
    focus_areas: List[str] = []


# ?????? Health ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

@app.get("/")
async def root():
    return {"service": "AutoGrader Feedback Generator", "status": "running", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ?????? Gemini call ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

def call_gemini_structured(prompt: str) -> Optional[dict]:
    """
    Call Gemini via REST and return parsed JSON dict, or None on failure.
    """
    if not GEMINI_API_KEY:
        return None
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3}
    }
    try:
        resp = httpx.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        raw = raw.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("` \n")
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Gemini feedback error: {e}")
        return None


def build_feedback_prompt(student_answer: str, expected_answer: str,
                           score: float, max_score: float,
                           rubric: str, errors: List[str], tone: str) -> str:
    error_section = "\n".join(f"- {e}" for e in errors) if errors else "None identified"
    return f"""You are a {tone} academic teacher providing feedback to a student.

### EXPECTED ANSWER:
{expected_answer}

### STUDENT ANSWER:
{student_answer}

### SCORE: {score}/{max_score}

### RUBRIC:
{rubric}

### IDENTIFIED ERRORS:
{error_section}

Task: Write structured feedback in the following JSON format ONLY (no markdown, no extra text):
{{
  "feedback": "A 2-3 sentence paragraph addressing the student directly.",
  "strengths": ["strength 1", "strength 2"],
  "areas_for_improvement": ["area 1", "area 2"],
  "suggestions": ["specific suggestion 1", "specific suggestion 2"]
}}

Be specific, constructive, and reference the actual content of their answer.
Tone should be {tone}."""


def build_improve_prompt(original_feedback: str, tone: str, focus_areas: List[str]) -> str:
    focus = ", ".join(focus_areas) if focus_areas else "general improvement"
    return f"""You are an experienced educator refining student feedback.

### ORIGINAL FEEDBACK:
{original_feedback}

### REQUESTED TONE: {tone}
### FOCUS AREAS: {focus}

Rewrite the feedback with the requested tone and focusing on: {focus}.
Return ONLY valid JSON (no markdown):
{{
  "feedback": "rewritten paragraph",
  "strengths": ["strength 1", ...],
  "areas_for_improvement": ["area 1", ...],
  "suggestions": ["suggestion 1", ...]
}}"""


# ?????? Endpoints ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

@app.post("/api/feedback/generate", response_model=FeedbackResponse)
async def generate_feedback(request: FeedbackRequest):
    """Generate structured personalised feedback using Gemini."""
    try:
        logger.info(f"Generating {request.tone} feedback for score {request.score}/{request.max_score}")

        prompt = build_feedback_prompt(
            request.student_answer,
            request.expected_answer,
            request.score,
            request.max_score,
            request.rubric_description,
            request.identified_errors,
            request.tone or "constructive"
        )

        result = call_gemini_structured(prompt)

        if result:
            return FeedbackResponse(
                feedback=result.get("feedback", ""),
                strengths=result.get("strengths", []),
                areas_for_improvement=result.get("areas_for_improvement", []),
                suggestions=result.get("suggestions", []),
                tone=request.tone or "constructive"
            )
        else:
            # Fallback: score-based heuristic
            pct = (request.score / request.max_score * 100) if request.max_score > 0 else 0
            if pct >= 90:
                feedback = "Excellent work! Your answer closely matches the reference solution."
                strengths = ["Strong conceptual understanding", "Correct methodology"]
                suggestions = ["Double-check units", "Review notation conventions"]
            elif pct >= 60:
                feedback = "Good effort. Some key concepts were captured but there are gaps to address."
                strengths = ["Partial concept alignment"]
                suggestions = ["Review the reference solution", "Check your derivation steps"]
            else:
                feedback = "This answer needs significant revision. Study the reference solution carefully."
                strengths = []
                suggestions = ["Review the fundamental concepts", "Practice more examples"]

            return FeedbackResponse(
                feedback=feedback,
                strengths=strengths,
                areas_for_improvement=request.identified_errors or ["Accuracy", "Completeness"],
                suggestions=suggestions,
                tone=request.tone or "constructive"
            )

    except Exception as e:
        logger.error(f"Error in generate_feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/feedback/improve", response_model=FeedbackResponse)
async def improve_feedback(request: ImproveFeedbackRequest):
    """
    Rewrite existing feedback with a different tone or focus.
    Useful for instructors who want to customise auto-generated feedback.
    """
    try:
        logger.info(f"Improving feedback with tone={request.tone_preference}, focus={request.focus_areas}")

        prompt = build_improve_prompt(
            request.original_feedback,
            request.tone_preference or "constructive",
            request.focus_areas
        )

        result = call_gemini_structured(prompt)

        if result:
            return FeedbackResponse(
                feedback=result.get("feedback", request.original_feedback),
                strengths=result.get("strengths", ["Good attempt"]),
                areas_for_improvement=result.get("areas_for_improvement", request.focus_areas),
                suggestions=result.get("suggestions", ["Review the material"]),
                tone=request.tone_preference or "constructive"
            )
        else:
            return FeedbackResponse(
                feedback=f"[{request.tone_preference}] {request.original_feedback}",
                strengths=["Effort demonstrated"],
                areas_for_improvement=request.focus_areas or ["Accuracy"],
                suggestions=["Review reference solution"],
                tone=request.tone_preference or "constructive"
            )

    except Exception as e:
        logger.error(f"Error in improve_feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)


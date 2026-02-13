from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoGrader Feedback Generator",
    description="AI-powered feedback generation for student submissions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FeedbackRequest(BaseModel):
    student_answer: str
    expected_answer: str
    score: float
    max_score: float
    rubric_description: str
    identified_errors: List[str] = []

class FeedbackResponse(BaseModel):
    feedback: str
    suggestions: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]
    tone: str  # constructive, encouraging, etc.

class ImproveFeedbackRequest(BaseModel):
    original_feedback: str
    tone_preference: Optional[str] = "constructive"
    focus_areas: List[str] = []

@app.get("/")
async def root():
    return {
        "service": "AutoGrader Feedback Generator",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def generate_feedback_prompt(student_answer: str, score: float, max_score: float, reasoning: str):
    return f"""
    You are a supportive and professional teacher. Provide feedback to a student based on their answer and the grading reasoning.

    ### STUDENT ANSWER:
    {student_answer}

    ### SCORE: {score}/{max_score}

    ### GRADING REASONING:
    {reasoning}

    ### TASK:
    Write a short, constructive feedback paragraph. Focus on strengths and specific areas for improvement.
    """

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    logger.warning("GEMINI_API_KEY not found. Feedback will use placeholders.")

def call_gemini_feedback(prompt: str):
    """Call Gemini API for natural language feedback."""
    try:
        if not api_key: return None
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        return None

@app.post("/api/feedback/generate", response_model=FeedbackResponse)
async def generate_feedback(request: FeedbackRequest):
    """
    Generate personalized feedback for student submission using Google Gemini API.
    """
    try:
        logger.info("Generating feedback with Google Gemini")
        
        prompt = generate_feedback_prompt(
            request.student_answer,
            request.score,
            request.max_score,
            ", ".join(request.identified_errors) if request.identified_errors else "N/A"
        )

        # Real AI Call
        ai_feedback = call_gemini_feedback(prompt)
        
        if ai_feedback:
            feedback_text = ai_feedback
            confidence = 0.95
        else:
            # Fallback
            feedback_text = "[Placeholder] Great effort! (API Key missing or error). Review your steps for minor errors."
            confidence = 0.5
        
        return FeedbackResponse(
            feedback=feedback_text,
            suggestions=["Review the reference solution for methodology", "Check calculations"],
            strengths=["Good structure", "Concept alignment"],
            areas_for_improvement=["Final accuracy"],
            tone="constructive"
        )
    except Exception as e:
        logger.error(f"Error generating feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback/improve", response_model=FeedbackResponse)
async def improve_feedback(request: ImproveFeedbackRequest):
    """
    Improve existing feedback based on preferences.
    
    TODO: Implement feedback refinement
    """
    try:
        logger.info(f"Improving feedback with tone: {request.tone_preference}")
        
        # Placeholder - return improved version
        return FeedbackResponse(
            feedback=f"[Improved with {request.tone_preference} tone]\n{request.original_feedback}",
            suggestions=["Study related examples", "Practice more problems"],
            strengths=["Good effort"],
            areas_for_improvement=["Calculation accuracy"],
            tone=request.tone_preference or "constructive"
        )
    except Exception as e:
        logger.error(f"Error improving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)

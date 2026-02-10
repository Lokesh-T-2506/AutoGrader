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

@app.post("/api/feedback/generate", response_model=FeedbackResponse)
async def generate_feedback(request: FeedbackRequest):
    """
    Generate personalized feedback for student submission.
    
    TODO: Implement:
    - GPT/LLM-based feedback generation
    - Template-based fallback
    - Tone adjustment
    - Personalization
    """
    try:
        logger.info("Generating feedback")
        
        # Placeholder feedback
        percentage = (request.score / request.max_score * 100) if request.max_score > 0 else 0
        
        feedback_text = f"""Great effort on this problem! You earned {request.score}/{request.max_score} points ({percentage:.1f}%).

STRENGTHS:
- Clear problem setup and identification of key variables
- Good understanding of fundamental concepts

AREAS FOR IMPROVEMENT:
- Pay attention to units in your final answer
- Show intermediate steps more clearly
- Double-check calculations for arithmetic errors

Keep practicing similar problems to strengthen your understanding!"""
        
        return FeedbackResponse(
            feedback=feedback_text,
            suggestions=[
                "Review unit conversions",
                "Practice showing detailed work",
                "Verify calculations step-by-step"
            ],
            strengths=[
                "Clear problem setup",
                "Good conceptual understanding"
            ],
            areas_for_improvement=[
                "Unit handling",
                "Showing intermediate steps",
                "Arithmetic accuracy"
            ],
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

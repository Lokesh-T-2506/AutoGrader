from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoGrader Grading Engine",
    description="Rubric-based grading using NLP and semantic similarity",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GradeRequest(BaseModel):
    student_answer: str
    reference_solution: str
    rubric_text: str
    use_partial_credit: bool = True

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
    criterion_scores: List[CriterionScore]
    overall_confidence: float

class RubricCriterion(BaseModel):
    id: str
    description: str
    max_points: float
    keywords: List[str]

class PartialCreditRequest(BaseModel):
    student_answer: str
    expected_answer: str
    rubric_criterion: RubricCriterion

class PartialCreditResponse(BaseModel):
    points_awarded: float
    percentage: float
    similarity_score: float
    matched_concepts: List[str]

@app.get("/")
async def root():
    return {
        "service": "AutoGrader Grading Engine",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def generate_grading_prompt(student_answer: str, reference_solution: str, rubric_text: str):
    return f"""
    You are an expert academic grader. Your task is to evaluate a student's answer based on a reference solution and specific grading instructions (rubric).

    ### REFERENCE SOLUTION (Ground Truth):
    {reference_solution}

    ### GRADING INSTRUCTIONS (Rubric):
    {rubric_text}

    ### STUDENT ANSWER:
    {student_answer}

    ### TASK:
    1. Compare the student answer to the reference solution.
    2. Follow the grading instructions strictly.
    3. Breakdown the score into criteria.
    4. Provide reasoning for each criterion.
    5. Output the result in JSON format.

    ### JSON FORMAT:
    {{
        "total_score": float,
        "max_score": float,
        "criterion_scores": [
            {{
                "criterion_id": "string",
                "points_awarded": float,
                "max_points": float,
                "confidence": float,
                "reasoning": "string",
                "matched_concepts": ["list", "of", "strings"]
            }}
        ],
        "overall_confidence": float
    }}
    """

import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash') # Using flash for speed/cost
else:
    logger.warning("GEMINI_API_KEY not found. LLM features will use placeholders.")

def call_gemini_grading(prompt: str):
    """Call Gemini API and return structured JSON."""
    try:
        if not api_key:
            return None
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1, # Keep it deterministic
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        return None

@app.post("/api/grade/evaluate", response_model=GradeResponse)
async def evaluate_submission(request: GradeRequest):
    """
    Evaluate student submission using Google Gemini API.
    """
    try:
        logger.info("Evaluating submission with Google Gemini API")
        
        prompt = generate_grading_prompt(
            request.student_answer, 
            request.reference_solution, 
            request.rubric_text
        )
        
        # Real AI Call
        ai_result = call_gemini_grading(prompt)
        
        if ai_result:
            # Parse AI JSON into DTOs
            criterion_scores = [
                CriterionScore(**score) for score in ai_result.get("criterion_scores", [])
            ]
            total = ai_result.get("total_score", 0.0)
            max_total = ai_result.get("max_score", 0.0)
            confidence = ai_result.get("overall_confidence", 0.90)
        else:
            # Fallback to placeholder if API fails or No Key
            logger.warning("Using placeholder grading logic (API failure or no key)")
            criterion_scores = [
                CriterionScore(
                    criterion_id="methodology",
                    points_awarded=4.0, max_points=5.0, confidence=0.92,
                    reasoning="[Placeholder] API Key missing. Please set GEMINI_API_KEY.",
                    matched_concepts=["placeholder"]
                )
            ]
            total, max_total, confidence = 4.0, 5.0, 0.5
        
        return GradeResponse(
            total_score=total,
            max_score=max_total,
            percentage=(total / max_total * 100) if max_total > 0 else 0,
            criterion_scores=criterion_scores,
            overall_confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error evaluating submission: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/grade/partial-credit", response_model=PartialCreditResponse)
async def calculate_partial_credit(request: PartialCreditRequest):
    """
    Calculate partial credit for a specific criterion.
    
    TODO: Implement semantic similarity calculation
    """
    try:
        logger.info("Calculating partial credit")
        
        # Placeholder response
        return PartialCreditResponse(
            points_awarded=request.rubric_criterion.max_points * 0.70,
            percentage=70.0,
            similarity_score=0.70,
            matched_concepts=request.rubric_criterion.keywords[:2]
        )
    except Exception as e:
        logger.error(f"Error calculating partial credit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

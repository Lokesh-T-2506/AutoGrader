"""
AutoGrader Analytics Engine v1.0
Synthesizes individual grading results into a Class Mastery JSON Report.
Final Year Project Intelligent Layer.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging
import os
import json
import httpx
from dotenv import load_dotenv

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="AutoGrader Analytics Engine",
    description="AI-driven Class Performance Summarizer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Data models ───────────────────────────────────────────────────────────────

class ResultEntry(BaseModel):
    student_id: str
    zone_id: str
    score: float
    max_score: float
    confidence: float
    reasoning: str
    concept: str

class AnalyticsRequest(BaseModel):
    results: List[ResultEntry]

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/analytics/summary")
async def generate_summary(request: AnalyticsRequest):
    """
    Deterministic Python Aggregation (Zero-Cost, 100% Reliable).
    """
    if not request.results:
        return {"error": "No results provided"}

    # 1. Basic Stats
    total_earned = sum(r.score for r in request.results)
    total_possible = sum(r.max_score for r in request.results)
    avg_pct = round((total_earned / total_possible * 100), 2) if total_possible > 0 else 0

    # 2. Concept Breakdown
    concepts = {}
    for r in request.results:
        if r.concept not in concepts:
            concepts[r.concept] = {"total": 0, "max": 0, "count": 0, "mistakes": []}
        c = concepts[r.concept]
        c["total"] += r.score
        c["max"] += r.max_score
        c["count"] += 1
        if r.score < r.max_score:
            c["mistakes"].append(r.reasoning[:100])

    breakdown = {}
    for name, data in concepts.items():
        avg = round((data["total"] / data["max"] * 100), 2) if data["max"] > 0 else 0
        mastery = "High" if avg >= 80 else ("Medium" if avg >= 50 else "Low")
        breakdown[name] = {
            "average_score": avg,
            "mastery_level": mastery,
            "common_misconception": data["mistakes"][0] if data["mistakes"] else "No major issues."
        }

    # 3. Student Identification
    student_totals = {}
    for r in request.results:
        if r.student_id not in student_totals:
            student_totals[r.student_id] = {"earned": 0, "max": 0}
        student_totals[r.student_id]["earned"] += r.score
        student_totals[r.student_id]["max"] += r.max_score

    top_performers = [sid for sid, data in student_totals.items() if (data["earned"]/data["max"]) >= 0.9]
    at_risk = [sid for sid, data in student_totals.items() if (data["earned"]/data["max"]) <= 0.4]

    # 4. Teacher Recommendation (Dynamic based on lowest concept)
    worst_concept = min(breakdown.items(), key=lambda x: x[1]["average_score"])[0] if breakdown else "N/A"
    recommendation = f"Refresher session recommended for '{worst_concept}' as class mastery is at {breakdown[worst_concept]['average_score']}%." if worst_concept != "N/A" else "Class performance is stable."

    return {
        "overall_average_pct": avg_pct,
        "concept_breakdown": breakdown,
        "top_performers": top_performers,
        "at_risk_students": at_risk,
        "teacher_recommendation": recommendation,
        "processing_engine": "Deterministic Python (Cost Optimized)"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)

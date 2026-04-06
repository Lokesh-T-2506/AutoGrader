# ⚡ AutoGrader Architectural Overview

## Multimodal Vision-First Pipeline

The AutoGrader architecture is designed to prioritize raw visual data over brittle OCR extraction. The following four-stage pipeline is orchestrated by the Spring Boot "Brain":

### 1. Vision Alignment (ORB-Based)
The **OCR Service (8001)** uses ORB feature matching to align the student paper to the instructor's template. 
- **Robustness**: ±80px padding is applied to handle rotation and skew.
- **Failover**: If ORB fails, the system uses an area-resizing fallback.

### 2. Intelligent Slicing
The aligned paper is sliced into discrete question zones (A, B, C...).
- **Dynamic Anchors**: Question anchors are discovered automatically via Printed OCR (PaddleOCR).
- **Vision-Optimized Crops**: Zones are saved as 60% quality JPEGs to balance upload speed with perfect AI clarity.

### 3. Generous AI Grading (Gemini 1.5 Flash/Pro)
The **Grading Engine (8003)** performs multimodal inference on each zone individually.
- **Resilient Serial Strategy**: Implements 15s cooling delays to respect API quotas while ensuring 100% processing of all zones.
- **"Extreme Generosity" Layer**: A pre-rubric directive forces the AI to award 10/10 for correctness and a baseline 7/10 for genuine attempts.

### 4. Direct Feedback Mapping
The orchestrator preserves the AI's "Reasoning" string and "Discovered Concept" for final reporting, ensuring that instructors can verify *why* points were awarded or deducted.

---

### Tech Stack
- **Backend Orchestrator**: Spring Boot v3.3.0 (Java 21)
- **Computer Vision**: OpenCV, PaddleOCR, FastAPI
- **Model Interface**: Google Gemini 1.5 (Multimodal Vision API)
- **Persistence**: H2 (In-memory for Demo Stability)

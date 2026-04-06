# ⚡ AutoGrader: Vision-First Multimodal AI Grading System

## Final Year Project Demo Edition (Hardened)

AutoGrader is a state-of-the-art, multimodal AI-driven system designed to automate the grading of handwritten physics and math assignments with human-level nuance and extreme resilience.

### 🌟 Key Vision-First Features
- **Multimodal AI Orchestration**: Leverages Gemini 1.5 Flash/Pro for direct visual analysis of student handwriting, bypassing traditional OCR failures.
- **Robust Alignment Engine**: Implements ORB-based feature matching with a ±80px robust padding system to handle skewed, rotated, or imperfectly scanned student papers.
- **Extreme Generosity Logic**: Programmatic grading rules ensure a 10/10 for correct work and a baseline 7/10 effort floor for any genuine student attempt.
- **Transparent Reasoning**: Full pass-through of AI feedback ("Why points were deducted") directly to the instructor dashboard.

### 🏗️ Modern Architecture
The system is built as a high-performance microservice ecosystem:
1. **Spring Boot Orchestrator (8080)**: The "Brain" that manages the 4-step pipeline (Align → Crop → Grade → Analytics).
2. **OCR & Alignment Service (8001)**: Handles computer vision tasks using PaddleOCR and OpenCV.
3. **Grading Service (8003)**: A resilient FastAPI bridge to the Gemini Vision API with built-in rate-limit cooling.
4. **Interactive Dashboard**: A professional vanilla JS frontend for real-time grading and class-level analytics.

### 🚀 Getting Started
1. **Launch ML Services**: `python run_services.py`
2. **Start Backend**: `cd backend && ./gradlew bootRun`
3. **Access Dashboard**: `http://localhost:8080/index.html`

 ---
**Project Status**: 🚀 Demo Ready (100% Verified)

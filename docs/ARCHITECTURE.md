# AutoGrader Architecture

## System Overview

AutoGrader is a microservices-based system for automated grading of handwritten assignments using AI/ML.

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React Frontend]
    end
    
    subgraph "Backend Layer"
        API[Spring Boot API]
        DB[(PostgreSQL)]
    end
    
    subgraph "ML Services Layer"
        OCR[OCR Service<br/>TrOCR + EasyOCR]
        MATH[Math Parser<br/>SymPy + Custom]
        GRADE[Grading Engine<br/>BERT + NLP]
        FEEDBACK[Feedback Gen<br/>GPT/LLM]
    end
    
    UI -->|HTTP/REST| API
    API -->|JDBC| DB
    API -->|REST| OCR
    API -->|REST| MATH
    API -->|REST| GRADE
    API -->|REST| FEEDBACK
    
    OCR -->|Text| MATH
    MATH -->|Parsed| GRADE
    GRADE -->|Scores| FEEDBACK

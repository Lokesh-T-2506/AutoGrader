# ML Services

Python-based microservices for machine learning operations in the AutoGrader system.

## 🏗️ Architecture

The ML services are designed as independent microservices that the backend communicates with via REST APIs:

```
├── ocr-service/          # Handwriting recognition (Port 8001)
├── math-parser/          # Mathematical expression parsing (Port 8002)
├── grading-engine/       # Rubric-based grading (Port 8003)
└── feedback-generator/   # AI feedback generation (Port 8004)
```

## 🚀 Services Overview

### 1. OCR Service (Port 8001)
**Purpose:** Extract text from handwritten submissions

**Technologies:**
- TrOCR (Microsoft Transformer-based OCR)
- EasyOCR (backup/comparison)
- OpenCV (preprocessing)
- Pillow (image handling)

**API Endpoints:**
- `POST /api/ocr/extract` - Extract text from image
- `POST /api/ocr/batch` - Batch process multiple images

### 2. Math Parser Service (Port 8002)
**Purpose:** Parse mathematical expressions into structured format

**Technologies:**
- Custom CNN + Attention models
- SymPy (symbolic math)
- LaTeX parsers
- Mathpix API integration (optional)

**API Endpoints:**
- `POST /api/math/parse` - Parse mathematical expression
- `POST /api/math/validate` - Validate mathematical syntax

### 3. Grading Engine (Port 8003)
**Purpose:** Match student answers against rubric criteria

**Technologies:**
- BERT/RoBERTa (semantic similarity)
- Sentence Transformers
- Custom scoring algorithms
- spaCy (NLP processing)

**API Endpoints:**
- `POST /api/grade/evaluate` - Evaluate submission against rubric
- `POST /api/grade/partial-credit` - Calculate partial credit

### 4. Feedback Generator (Port 8004)
**Purpose:** Generate personalized feedback for students

**Technologies:**
- GPT API or local LLM
- Fine-tuned T5 models
- Template-based generation

**API Endpoints:**
- `POST /api/feedback/generate` - Generate feedback
- `POST /api/feedback/improve` - Improve existing feedback

## 📦 Setup

### Prerequisites
- Python 3.10+
- CUDA (optional, for GPU acceleration)
- 8GB+ RAM (16GB+ recommended)

### Installation

Each service can be set up independently:

```bash
# OCR Service
cd ocr-service
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py

# Repeat for other services...
```

### Docker Setup

```bash
# Build all services
docker-compose build

# Run all services
docker-compose up
```

## 🧪 Testing

Each service includes test scripts:

```bash
cd ocr-service
pytest tests/
```

## 📊 Performance Benchmarks

Target performance metrics:
- **OCR Service:** < 2s per page
- **Math Parser:** < 1s per expression
- **Grading Engine:** < 3s per submission
- **Feedback Generator:** < 5s per submission

## 🔧 Configuration

Each service has a `config.yaml` for customization:
- Model selection
- Confidence thresholds
- GPU/CPU settings
- API keys (if using external services)

## 📚 Development

### Adding a New Service

1. Create directory: `new-service/`
2. Add FastAPI application
3. Implement API endpoints
4. Add to docker-compose
5. Update documentation

### Model Training

Training scripts are in `notebooks/` for each service:
- Data preparation
- Model training
- Evaluation
- Export for deployment

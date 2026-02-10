# AutoGrader

> Automated grading system for handwritten assignments using AI/ML

## 🎯 Project Overview

AutoGrader addresses the time-consuming challenge of grading handwritten assignments in physics and problem-solving courses. The system uses machine learning to assist instructors in evaluating handwritten student work with predefined rubrics while supporting partial credit and detailed feedback.

## 🏗️ Architecture

```
AutoGrader/
├── backend/              # Spring Boot API (Java 17)
├── ml-services/          # Python ML microservices
│   ├── ocr-service/      # Handwriting recognition
│   ├── math-parser/      # Mathematical expression parsing
│   ├── grading-engine/   # Rubric-based evaluation
│   └── feedback-generator/ # AI-powered feedback
└── frontend/             # React UI (coming soon)
```

## 🛠️ Technology Stack

### Backend
- **Framework:** Spring Boot 3.x
- **Language:** Java 17
- **Database:** PostgreSQL
- **Build Tool:** Gradle
- **Key Dependencies:** Spring Web, Spring Data JPA, Spring Security

### ML Services
- **Framework:** FastAPI (Python 3.10+)
- **OCR:** TrOCR, EasyOCR
- **Math Recognition:** Custom models, Mathpix API
- **NLP:** BERT, Sentence Transformers
- **ML Frameworks:** PyTorch, TensorFlow
- **Computer Vision:** OpenCV

## 🚀 Quick Start

### Prerequisites
- Java 17+
- Python 3.10+
- PostgreSQL 14+
- Docker (optional)

### Backend Setup
```bash
cd backend
./gradlew bootRun
```

### ML Services Setup
```bash
cd ml-services/ocr-service
pip install -r requirements.txt
python main.py
```

## 📋 Development Phases

### Phase 1: MVP (Current Focus)
- [x] Project scaffolding
- [ ] Basic OCR functionality
- [ ] Simple rubric matching
- [ ] File upload/storage
- [ ] Manual review interface

### Phase 2: Enhanced Grading
- [ ] Mathematical expression recognition
- [ ] Advanced NLP-based grading
- [ ] Partial credit algorithms
- [ ] Automated feedback generation

### Phase 3: Production Ready
- [ ] Custom model training
- [ ] Batch processing optimization
- [ ] Full frontend implementation
- [ ] Deployment pipeline

## 📚 Documentation

- [Backend Documentation](./backend/README.md)
- [ML Services Documentation](./ml-services/README.md)
- [Architecture Overview](./docs/ARCHITECTURE.md)

## 🤝 Contributing

This is an academic project. Contributions and suggestions are welcome!

## 📄 License

MIT License

## 👨‍💻 Author

Built as a solution to improve the grading experience in large physics courses.

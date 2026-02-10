# AutoGrader Setup Guide

## 🚀 Quick Start Guide

This guide will help you get AutoGrader up and running on your local machine.

## Prerequisites

### Required Software
- **Java 17+** (for Spring Boot backend)
- **Python 3.10+** (for ML services)
- **PostgreSQL 14+** (database)
- **Git** (version control)

### Optional
- **Docker & Docker Compose** (recommended for easier setup)
- **CUDA** (for GPU acceleration in ML models)

## Setup Options

### Option 1: Docker Setup (Recommended for Testing)

1. **Clone the repository:**
```bash
cd C:\Users\tallu\OneDrive\Desktop\AutoGrader
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Verify services are running:**
```bash
docker-compose ps
```

You should see:
- `autograder-backend` on port 8080
- `autograder-postgres` on port 5432
- `autograder-ocr` on port 8001
- `autograder-math-parser` on port 8002
- `autograder-grading` on port 8003
- `autograder-feedback` on port 8004

4. **Test the backend:**
```bash
curl http://localhost:8080/api/submissions/1
```

### Option 2: Local Development Setup

#### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Install PostgreSQL and create database:**
```sql
CREATE DATABASE autograder;
```

3. **Update `application.properties`:**
```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/autograder
spring.datasource.username=YOUR_USERNAME
spring.datasource.password=YOUR_PASSWORD
```

4. **Run the backend:**
```bash
.\gradlew.bat bootRun
```

Backend will start on `http://localhost:8080`

#### ML Services Setup

For each service (ocr-service, math-parser, grading-engine, feedback-generator):

1. **Navigate to service directory:**
```bash
cd ml-services\ocr-service
```

2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the service:**
```bash
python main.py
```

Repeat for all ML services on their respective ports:
- OCR Service: 8001
- Math Parser: 8002
- Grading Engine: 8003
- Feedback Generator: 8004

## Verification

### Test Backend API
```bash
curl http://localhost:8080/api/grading/jobs/1
```

### Test OCR Service
```bash
curl http://localhost:8001/health
```

### Test Math Parser
```bash
curl http://localhost:8002/health
```

### Test Grading Engine
```bash
curl http://localhost:8003/health
```

### Test Feedback Generator
```bash
curl http://localhost:8004/health
```

## Next Steps

1. **Implement OCR Models:** Start with TrOCR implementation in `ml-services/ocr-service/models.py`
2. **Add Sample Data:** Create test datasets for training and evaluation
3. **Build Frontend:** Create React UI for instructors and students
4. **Deploy:** Set up production deployment pipeline

## Common Issues

### Database Connection Failed
- Ensure PostgreSQL is running
- Check credentials in `application.properties`
- Verify database exists

### ML Service Port Already in Use
- Check if another service is using the port: `netstat -ano | findstr :8001`
- Kill the process or change the port in the service's `main.py`

### Python Dependencies Installation Failed
- Ensure Python 3.10+ is installed
- Try upgrading pip: `python -m pip install --upgrade pip`
- For PyTorch issues, visit: https://pytorch.org/get-started/locally/

## Development Workflow

1. **Start Database:** `docker start autograder-postgres` (if using Docker)
2. **Start Backend:** `cd backend && .\gradlew.bat bootRun`
3. **Start ML Services:** Run each service in separate terminals
4. **Make Changes:** Edit code in your IDE
5. **Test:** Use Postman or curl to test API endpoints
6. **Iterate:** Repeat the cycle

## Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [TrOCR Model](https://huggingface.co/microsoft/trocr-base-handwritten)
- [Sentence Transformers](https://www.sbert.net/)

---

**Ready to build?** Start with implementing the OCR service - that's the foundation for everything else! 🚀

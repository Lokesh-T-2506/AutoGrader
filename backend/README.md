# AutoGrader Backend

Spring Boot REST API for managing assignments, submissions, and grading workflows.

## 🏗️ Architecture

### Core Components
- **Assignment Management:** Create/manage assignments and rubrics
- **Submission Handler:** Upload and process student submissions
- **Job Queue:** Async grading job processing
- **Results API:** Retrieve grading results and feedback
- **User Management:** Authentication and authorization

### Database Schema

```
User (id, email, role, name)
Course (id, name, instructor_id)
Assignment (id, course_id, title, rubric_json, due_date)
Submission (id, assignment_id, student_id, file_path, submitted_at)
GradingJob (id, submission_id, status, created_at)
GradingResult (id, job_id, score, feedback_json, confidence)
```

## 🚀 Getting Started

### Prerequisites
- Java 17 or higher
- PostgreSQL 14+
- Gradle 8.x

### Setup

1. **Install dependencies:**
```bash
./gradlew build
```

2. **Configure database:**
Create a PostgreSQL database and update `application.properties`:
```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/autograder
spring.datasource.username=your_username
spring.datasource.password=your_password
```

3. **Run the application:**
```bash
./gradlew bootRun
```

The API will be available at `http://localhost:8080`

## 📡 API Endpoints

### Assignments
- `POST /api/assignments` - Create assignment
- `GET /api/assignments/{id}` - Get assignment details
- `PUT /api/assignments/{id}` - Update assignment

### Submissions
- `POST /api/submissions` - Upload submission
- `GET /api/submissions/{id}` - Get submission details
- `GET /api/assignments/{id}/submissions` - List submissions

### Grading
- `POST /api/grading/jobs` - Create grading job
- `GET /api/grading/jobs/{id}` - Get job status
- `GET /api/grading/results/{id}` - Get grading results

## 🧪 Testing

```bash
./gradlew test
```

## 📦 Build

```bash
./gradlew build
```

## 🐳 Docker

```bash
docker build -t autograder-backend .
docker run -p 8080:8080 autograder-backend
```

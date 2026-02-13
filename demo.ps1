# AutoGrader Phase 1 Demo Script
# Requires all services (8080, 8001, 8003, 8004) to be running.

$BaseUrl = "http://localhost:8080/api"

Write-Host "--- AutoGrader Phase 1 Demo ---" -ForegroundColor Cyan

# 1. Create a Course
Write-Host "Creating Course..."
$course = Invoke-RestMethod -Method Post -Uri "$BaseUrl/courses" -ContentType "application/json" -Body '{
    "name": "Introduction to AI",
    "description": "Learning about OCR and LLMs",
    "instructorId": 1
}'
Write-Host "Course Created: $($course.name) (ID: $($course.id))"

# 2. Create an Assignment
Write-Host "Creating Assignment with Rubric..."
$assignment = Invoke-RestMethod -Method Post -Uri "$BaseUrl/assignments" -ContentType "application/json" -Body "{
    \"courseId\": $($course.id),
    \"title\": \"Calculus Quiz 1\",
    \"description\": \"Solve the integral of x^2\",
    \"totalPoints\": 10.0,
    \"rubricText\": \"Check for power rule application. Give 5 points for correct derivative, 5 for final answer.\",
    \"referenceSolutionText\": \"The integral of x^2 is (x^3)/3 + C. Derivative check: d/dx((x^3)/3) = x^2.\"
}"
Write-Host "Assignment Created: $($assignment.title) (ID: $($assignment.id))"

# 3. Create a Submission (Simulated)
# In a real scenario, this would involve a file upload.
Write-Host "Creating Student Submission..."
$submission = Invoke-RestMethod -Method Post -Uri "$BaseUrl/submissions" -ContentType "application/json" -Body "{
    \"assignmentId\": $($assignment.id),
    \"studentId\": 101,
    \"filePath\": \"c:/Users/tallu/OneDrive/Desktop/AutoGrader/backend/uploads/sample_submission.png\"
}"
Write-Host "Submission Created (ID: $($submission.id))"

# 4. Trigger Grading
Write-Host "Triggering Automated AI Grading..."
$job = Invoke-RestMethod -Method Post -Uri "$BaseUrl/grading/jobs" -ContentType "application/json" -Body "{
    \"submissionId\": $($submission.id)
}"
Write-Host "Grading Job Started (ID: $($job.id))"

Write-Host "`nWaiting for AI to finish (OCR + Gemini)..."
Start-Sleep -Seconds 10

# 5. Fetch Results
Write-Host "Fetching Results from H2 Database..."
$result = Invoke-RestMethod -Method Get -Uri "$BaseUrl/grading/jobs/$($job.id)"
Write-Host "`n--- GRADING RESULT ---" -ForegroundColor Green
Write-Host "Score: $($result.score) / $($result.maxScore)"
Write-Host "Feedback: $($result.feedbackJson)"
Write-Host "OCR Transcribed Text: $($result.ocrText)"
Write-Host "--------------------"

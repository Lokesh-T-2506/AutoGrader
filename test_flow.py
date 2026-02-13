import requests
import json
import time

BASE_URL = "http://localhost:8080/api"

def run_demo():
    print("--- AutoGrader Phase 1 Demo (Python version) ---")
    
    try:
        # 0. Create a User (Instructor)
        print("\n0. Creating Instructor User...")
        user_data = {
            "email": "professor@demo.edu",
            "password": "password123",
            "name": "Dr. AI Demo",
            "role": "INSTRUCTOR"
        }
        res = requests.post(f"{BASE_URL}/users", json=user_data)
        res.raise_for_status()
        user = res.json()
        user_id = user["id"]
        print(f"   Success! Instructor created with ID: {user_id}")

        # 1. Create a Course (SKIPPED - Simplified Model)
        # print("\n1. Creating Course...")
        # course_id = 999 
        print("   Skipping Course creation (Global Assignment mode)")

        # 1.5 Create a Student User
        print("\n1.5 Creating Student User...")
        student_data = {
            "email": "student@demo.edu",
            "password": "password123",
            "name": "Student A",
            "role": "STUDENT"
        }
        res = requests.post(f"{BASE_URL}/users", json=student_data)
        res.raise_for_status()
        student = res.json()
        student_id = student["id"]
        print(f"   Success! Student created with ID: {student_id}")

        # 2. Create an Assignment
        print("\n2. Creating Assignment with Rubric...")
        assignment_data = {
            # "courseId": course_id,  <-- REMOVED
            "title": "Calculus Quiz",
            "description": "Integration of x^2",
            "totalPoints": 10.0,
            "rubricText": "Award 5 points for using the power rule correctly, and 5 points for the correct final answer (x^3 / 3 + C).",
            "referenceSolutionText": "(x^3)/3 + C"
        }
        res = requests.post(f"{BASE_URL}/assignments", json=assignment_data)
        res.raise_for_status()
        assignment = res.json()
        assignment_id = assignment["id"]
        print(f"   Success! Assignment created with ID: {assignment_id}")
        
        # 3. Create a Submission
        print("\n3. Creating Submission...")
        
        file_path = r"c:\Users\tallu\OneDrive\Desktop\AutoGrader\backend\uploads\sample_submission.png"
        
        # Open file in binary mode
        with open(file_path, "rb") as f:
            files = {"file": ("sample_submission.png", f, "image/png")}
            data = {
                "assignmentId": assignment_id,
                "studentId": student_id 
            }
            # Note: Do not set Content-Type header manually; requests does it with boundary
            res = requests.post(f"{BASE_URL}/submissions", files=files, data=data)
            
        res.raise_for_status()
        submission = res.json()
        submission_id = submission["id"]
        print(f"   Success! Submission created with ID: {submission_id}")
        
        # 4. Trigger Grading Job
        print("\n4. Triggering AI Grading Job...")
        res = requests.post(f"{BASE_URL}/grading/jobs", json={"submissionId": submission_id})
        res.raise_for_status()
        job = res.json()
        job_id = job["id"]
        print(f"   Success! Grading job started with ID: {job_id}")
        
        print("\nWaiting for AI processing (OCR + Gemini)... (20 seconds)")
        time.sleep(20)
        
        # 5. Fetch Results
        print("\n5. Fetching Results...")
        res = requests.get(f"{BASE_URL}/grading/jobs/{job_id}")
        res.raise_for_status()
        result = res.json()
        
        print("\n========================================")
        print("          FINAL GRADING RESULT          ")
        print("========================================")
        print(f"Status:   {result.get('status')}")
        print(f"Score:    {result.get('score')} / {result.get('maxScore')}")
        print(f"OCR Text: {result.get('ocrText')}")
        print(f"Feedback: {result.get('feedbackJson')}")
        print("========================================")
        
    except Exception as e:
        print(f"\nERROR: Demo failed. Details: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Server Response: {e.response.text}")

if __name__ == "__main__":
    run_demo()

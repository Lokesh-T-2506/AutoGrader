import requests
import os
import time
import json
from pathlib import Path

# Configuration
SERVICES = {
    "ocr": "http://localhost:8001",
    "math": "http://localhost:8002",
    "grading": "http://localhost:8003"
}

SAMPLE_DIR = Path("ml-services/data/samples")
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

def health_check():
    print("=== Service Health Check ===")
    for name, url in SERVICES.items():
        try:
            resp = requests.get(f"{url}/health", timeout=5)
            status = "UP" if resp.status_code == 200 else f"DOWN ({resp.status_code})"
            print(f"{name.upper():<10}: {status}")
        except Exception as e:
            print(f"{name.upper():<10}: DOWN (Error: {str(e)})")
    print("-" * 30)

def test_ocr_service(image_path):
    print(f"Testing OCR Service with: {image_path}")
    url = f"{SERVICES['ocr']}/api/ocr/extract"
    
    if not os.path.exists(image_path):
        print(f"Error: Image {image_path} not found.")
        return None

    with open(image_path, "rb") as f:
        files = {"file": f}
        start = time.time()
        response = requests.post(url, files=files)
        duration = time.time() - start
        
    if response.status_code == 200:
        data = response.json()
        print(f"Result: '{data['text']}' (Confidence: {data['confidence']})")
        print(f"Latency: {duration:.2f}s")
        return data['text']
    else:
        print(f"OCR Error: {response.text}")
        return None

def test_math_parser(expression):
    print(f"Testing Math Parser with: {expression}")
    url = f"{SERVICES['math']}/api/math/parse"
    payload = {"expression": expression, "context": "physics quiz"}
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"Parsed LaTeX: {data['latex']}")
        print(f"Symbolic: {data['symbolic']}")
        return data
    else:
        print(f"Math Parser Error: {response.text}")
        return None

def test_grading_engine(student_answer, reference, rubric):
    print("Testing Grading Engine...")
    url = f"{SERVICES['grading']}/api/grade/evaluate"
    payload = {
        "student_answer": student_answer,
        "reference_solution": reference,
        "rubric_text": rubric,
        "use_partial_credit": True
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"Score: {data['total_score']}/{data['max_score']} ({data['percentage']}%)")
        print(f"Confidence: {data['overall_confidence']}")
        return data
    else:
        print(f"Grading Error: {response.text}")
        return None

def run_full_pipeline(student_img, instructor_img):
    print("\n" + "="*50)
    print("RUNNING END-TO-END TA GRADING PIPELINE TEST")
    print("="*50)
    
    # 1. OCR Instructor Solution (Reference)
    print("\n[Step 1/3] OCRing Instructor's Reference Solution...")
    instructor_text = test_ocr_service(instructor_img)
    if not instructor_text: 
        print("Failed to OCR instructor solution. Using fallback.")
        instructor_text = "The integral of x^2 is (x^3)/3 + C"
    
    # 2. OCR Student Submission
    print("\n[Step 2/3] OCRing Student Submission...")
    student_text = test_ocr_service(student_img)
    if not student_text: return
    
    # 3. Math Parsing (Optional check for symbolic correctness)
    test_math_parser(student_text)
    
    # 4. Grading
    print("\n[Step 3/3] Evaluating with TA Context...")
    rubric = "1. Correct integration (3 pts), 2. Constant of integration included (1 pt)"
    
    grade = test_grading_engine(student_text, instructor_text, rubric)
    
    print("\n" + "="*50)
    print("TA PIPELINE TEST COMPLETE")
    print("="*50)

if __name__ == "__main__":
    # Check if services are up first
    health_check()
    
    # Sample images
    # We use the same image for both as a 'perfect match' test case
    student_sample = "backend/uploads/sample_submission.png"
    instructor_sample = "backend/uploads/sample_submission.png" 
    
    if os.path.exists(student_sample):
        run_full_pipeline(student_sample, instructor_sample)
    else:
        print(f"\nNo sample image found. Please run 'python generate_sample.py' first.")

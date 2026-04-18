import requests
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Create a simple test PDF
pdf_buffer = io.BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=letter)
c.drawString(100, 750, "Test PDF Document")
c.drawString(100, 730, "This is a sample PDF for testing BYOM upload.")
c.drawString(100, 710, "")
c.drawString(100, 690, "Key Concepts:")
c.drawString(100, 670, "1. The mitochondria is the powerhouse of the cell")
c.drawString(100, 650, "2. It generates ATP for energy")
c.drawString(100, 630, "3. It has its own DNA")
c.showPage()
c.save()
pdf_buffer.seek(0)

# Test 1: Upload PDF
print("Test 1: Uploading PDF...")
files = {'file': ('test_document.pdf', pdf_buffer, 'application/pdf')}
response = requests.post("http://127.0.0.1:8000/upload-byom", files=files)
print(f"Upload response: {response.status_code} - {response.json()}")

# Test 2: Get level test for BYOM
print("\nTest 2: Getting BYOM level test...")
response = requests.get("http://127.0.0.1:8000/level-test?subject=BYOM")
print(f"Level test questions: {len(response.json()['questions'])} questions")

# Test 3: Ask a question to BYOM
print("\nTest 3: Asking question to BYOM...")
response = requests.get(
    "http://127.0.0.1:8000/ask",
    params={
        "user_query": "What is the powerhouse of the cell?",
        "student_level": "Intermediate",
        "grade": "BYOM",
        "subject": "BYOM",
        "chapter": "Uploaded Document"
    }
)
result = response.json()
print(f"Response status: {response.status_code}")
print(f"Title: {result.get('title')}")
print(f"Flashcards: {len(result.get('flashcards', []))} card(s)")
print(f"Has visual blueprint: {'visual' in result}")
print(f"Quiz included: {'quiz' in result}")
print("\n✅ BYOM flow test complete!")

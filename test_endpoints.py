import requests
import json

print("=" * 60)
print("Testing /grades endpoint")
print("=" * 60)
response = requests.get("http://127.0.0.1:8000/grades")
print("Status Code:", response.status_code)
print("Response:", json.dumps(response.json(), indent=2))

print("\n" + "=" * 60)
print("Testing /ask endpoint (exact match: Cell Structure)")
print("=" * 60)
response = requests.get(
    "http://127.0.0.1:8000/ask",
    params={
        "user_query": "What is mitochondria",
        "student_level": "Intermediate",
        "grade": "Grade 6",
        "subject": "science",
        "chapter": "Cell Structure"
    }
)
print("Status Code:", response.status_code)
result = response.json()
print("Response keys:", list(result.keys()))
print("Has title:", "title" in result)
print("Has flashcards:", "flashcards" in result)
if "title" in result:
    print("Title:", result["title"])

print("\n" + "=" * 60)
print("Testing /ask endpoint (fallback match: Non-existent chapter)")
print("=" * 60)
response = requests.get(
    "http://127.0.0.1:8000/ask",
    params={
        "user_query": "What is mitochondria",
        "student_level": "Intermediate",
        "grade": "Grade 6",
        "subject": "science",
        "chapter": "Nonexistent Chapter"
    }
)
print("Status Code:", response.status_code)
result = response.json()
print("Response keys:", list(result.keys()))
if "error" in result:
    print("Error message:", result["error"])
else:
    print("Title (fallback response):", result.get("title", "N/A"))

print("\n✅ All endpoint tests completed!")

import requests

# Test level-test for BYOM
response = requests.get("http://127.0.0.1:8000/level-test?subject=BYOM")
print("Level test response:", response.json())

# Test grades
response = requests.get("http://127.0.0.1:8000/grades")
print("Grades response:", response.json())

# Test ask with BYOM
response = requests.get("http://127.0.0.1:8000/ask?user_query=What is the powerhouse of the cell&student_level=Intermediate&grade=BYOM&subject=BYOM&chapter=Uploaded Document")
print("Ask BYOM response:", response.json())
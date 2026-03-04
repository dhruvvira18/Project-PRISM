import os
import json
import statistics
import chromadb
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY")
print("API KEY LOADED:", API_KEY is not None)
client_ai = genai.Client(api_key=API_KEY)

client_db = chromadb.PersistentClient(path="./db")
try:
    collection = client_db.get_collection(name="grade6_syllabus")
except Exception:
    print("⚠️ WARNING: Collection not found. Run ingest.py first!")
    collection = None


# --- NEW MOCK DATABASE FOR LEVEL TESTS ---
SUBJECTS_DB = {
    "Science": [
        {
            "question": "What is friction?",
            "options": [
                {"text": "It slows objects down.", "difficulty": 1},
                {"text": "A force that resists motion.", "difficulty": 2},
                {"text": "A force between two surfaces in contact.", "difficulty": 3},
                {"text": "A resistive force opposing relative motion.", "difficulty": 4}
            ]
        },
        {
            "question": "Why do plants need sunlight?",
            "options": [
                {"text": "To stay warm and grow.", "difficulty": 1},
                {"text": "To make their own food.", "difficulty": 2},
                {"text": "To perform photosynthesis and make glucose.", "difficulty": 3},
                {"text": "To convert solar energy into chemical energy.", "difficulty": 4}
            ]
        },
        {
            "question": "What happens when water boils?",
            "options": [
                {"text": "It gets really hot and bubbles.", "difficulty": 1},
                {"text": "It turns into steam or gas.", "difficulty": 2},
                {"text": "It changes state from liquid to gas.", "difficulty": 3},
                {"text": "The molecules gain enough kinetic energy to overcome intermolecular forces.", "difficulty": 4}
            ]
        },
        {
            "question": "What is a magnetic field?",
            "options": [
                {"text": "The area where a magnet pulls things.", "difficulty": 1},
                {"text": "The invisible space around a magnet.", "difficulty": 2},
                {"text": "A region where magnetic materials experience a force.", "difficulty": 3},
                {"text": "A vector field that describes the magnetic influence on moving electric charges.", "difficulty": 4}
            ]
        }
    ],
    "Social Studies": [
        {
            "question": "What is a democracy?",
            "options": [
                {"text": "When people vote for things.", "difficulty": 1},
                {"text": "A system where people choose their leaders.", "difficulty": 2},
                {"text": "A government elected by the citizens of a country.", "difficulty": 3},
                {"text": "A system of governance by the whole population, typically through elected representatives.", "difficulty": 4}
            ]
        },
        {
            "question": "Why do we have laws?",
            "options": [
                {"text": "To keep people out of trouble.", "difficulty": 1},
                {"text": "To make sure everyone plays fair.", "difficulty": 2},
                {"text": "To maintain order and protect citizens' rights.", "difficulty": 3},
                {"text": "To provide a structured legal framework that governs societal behavior.", "difficulty": 4}
            ]
        },
        {
            "question": "What is a map scale?",
            "options": [
                {"text": "It tells you how big things are.", "difficulty": 1},
                {"text": "A way to measure distance on a map.", "difficulty": 2},
                {"text": "The ratio of a distance on the map to the real distance.", "difficulty": 3},
                {"text": "The proportional relationship between map dimensions and actual Earth dimensions.", "difficulty": 4}
            ]
        },
        {
            "question": "What does a historian do?",
            "options": [
                {"text": "Reads about old stuff.", "difficulty": 1},
                {"text": "Studies things that happened in the past.", "difficulty": 2},
                {"text": "Researches and writes about historical events.", "difficulty": 3},
                {"text": "Analyzes primary and secondary sources to construct historical narratives.", "difficulty": 4}
            ]
        }
    ]
}

class LevelAnswers(BaseModel):
    answers: list[int]

# --- NEW ENDPOINTS ---

@app.get("/subjects")
async def get_subjects():
    return {"subjects": list(SUBJECTS_DB.keys())}

@app.get("/level-test")
async def get_level_test(subject: str = Query(...)):
    questions = SUBJECTS_DB.get(subject, [])
    if not questions:
        return JSONResponse(status_code=404, content={"error": "Subject not found."})
    return {"subject": subject, "questions": questions}

@app.post("/calculate-level")
async def calculate_level(data: LevelAnswers):
    if not data.answers:
        return {"level": "Intermediate", "median_score": 3}
    
    med = statistics.median(data.answers)
    
    if med <= 2:
        level = "Beginner"
    elif med <= 3:
        level = "Intermediate"
    else:
        level = "Advanced"
        
    return {"level": level, "median_score": med}


# --- EXISTING ENDPOINTS ---

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/ask")
async def ask_assistant(user_query: str = Query(...), student_level: str = Query("Intermediate")):
    if not collection:
        return JSONResponse(status_code=500, content={"title": "Error", "flashcard_content": "Database not initialized."})

    try:
        results = collection.query(query_texts=[user_query], n_results=2)
        context = " ".join(results['documents'][0]) if results['documents'] else "No context found."

        prompt = f"""
        ROLE: Grade 6 ADHD Study Mentor.
        STUDENT_LEVEL: {student_level}
        CONTEXT: {context}
        QUERY: {user_query}
        
        RULES: 
        1. NO Bionic Reading. 
        2. Use standard bolding for **Full Keywords**.
        3. Return ONLY valid JSON.
        4. Create a multiple-choice quiz based on the context.
        5. Adjust explanation complexity according to the STUDENT_LEVEL.
           - Beginner -> very simple, highly accessible explanation.
           - Intermediate -> normal, grade-level explanation.
           - Advanced -> deeper, more conceptual explanation.

        RETURN ONLY JSON:
        {{
          "title": "Topic Name",
          "flashcard_content": "Bite-sized explanation matching the student level with **Keywords** bolded.",
          "key_points": ["Point 1", "Point 2", "Point 3"],
          "analogy": "A clear metaphor matching the student's level",
          "breadcrumb": "Grade 6 > Subject > Chapter",
          "quiz": {{
            "question": "A clear question based on the text.",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct": "Exact string of the correct option",
            "explanation": "Brief explanation of why this answer is correct."
          }}
        }}"""

        response = client_ai.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )

        text_response = response.text.strip()
        if "```json" in text_response:
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif "```" in text_response:
            text_response = text_response.split("```")[1].split("```")[0].strip()
        
        return JSONResponse(content=json.loads(text_response))

    except Exception as e:
        print(f"❌ BACKEND ERROR: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
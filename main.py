import os
import statistics
import chromadb
import json
import logging
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Import our separated AI logic (Updated path: generator is in the root directory)
from codebase.generator import get_prism_content_from_db

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB connection once on startup
# Using the persistent path and collection name from your latest ingest.py
client_db = chromadb.PersistentClient(path="./prism_db")
try:
    collection = client_db.get_collection(name="prism_curriculum")
    logging.info("Successfully connected to ChromaDB 'prism_curriculum'")
except Exception:
    logging.warning("Collection 'prism_curriculum' not found. Run ingest.py first!")
    collection = None

# --- MOCK DATABASE FOR LEVEL TESTS ---
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

# --- ENDPOINTS ---

@app.get("/grades")
async def get_grades():
    return {"grades": ["Grade 5", "Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10"]}

@app.get("/subjects")
async def get_subjects(grade: str = Query(...)):
    # Assuming all grades have Science and Social Studies
    return {"subjects": ["Science", "Social Studies"]}

@app.get("/level-test")
async def get_level_test(subject: str = Query(...)):
    questions = SUBJECTS_DB.get(subject, [])
    if not questions:
        return JSONResponse(status_code=404, content={"error": "Subject not found."})
    return {"subject": subject, "questions": questions}

@app.post("/calculate-level")
async def calculate_level(data: LevelAnswers):
    if not data.answers:
        logging.warning("No answers provided, defaulting to Intermediate.")
        return {"level": "Intermediate", "median_score": 3}
    
    med = statistics.median(data.answers)
    if med <= 2:
        level = "Beginner"
    elif med <= 3:
        level = "Intermediate"
    else:
        level = "Advanced"
        
    return {"level": level, "median_score": med}

# --- AI CORE ENDPOINT ---

@app.get("/ask")
async def ask_assistant(user_query: str = Query(..., min_length=1, max_length=500), 
                        student_level: str = Query("Intermediate", pattern="^(Beginner|Intermediate|Advanced)$")):
    
    if not collection:
        return JSONResponse(status_code=500, content={"error": "Database not initialized. Please run ingest.py."})

    try:
        # Call the separated logic
        ai_data = get_prism_content_from_db(user_query, student_level, collection)
        return JSONResponse(content=ai_data)
        
    except ValueError as ve:
        logging.error(f"Validation error: {str(ve)}")
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from AI response")
        return JSONResponse(status_code=500, content={"error": "Invalid AI response format"})
    except Exception as e:
        logging.error(f"Backend error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/session-stats")
async def get_session_stats():
    """Session statistics for progress tracking (ADHD motivation boost)."""
    return {
        "topics_learned": 0,
        "questions_correct": 0,
        "streak": 0,
        "session_minutes": 0,
        "next_milestone": "Learn your first topic to unlock 'Knowledge Seeker' badge! 🎓"
    }

# --- STATIC FILES AND TEMPLATE ROUTING ---

# 1. Get the absolute path to the directory containing main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Define exactly where the static folder is (in the root directory)
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 3. Mount the static directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def read_index():
    # 4. Point to the templates folder inside codebase
    template_path = os.path.join("codebase", "templates", "index.html")
    return FileResponse(template_path)
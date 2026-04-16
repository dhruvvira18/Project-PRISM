import os
import statistics
import chromadb
import json
import logging
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

from generator import get_prism_content_from_db

logging.basicConfig(level=logging.INFO)

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    logging.warning("Supabase credentials missing! Dynamic DB fetches will fail.")
    supabase = None

client_db = chromadb.PersistentClient(path="./prism_db")
try:
    collection = client_db.get_collection(name="prism_curriculum")
except Exception:
    collection = None

class LevelAnswers(BaseModel):
    answers: list[int]

# --- SUPABASE DYNAMIC ENDPOINTS (WITH SAFE FALLBACKS) ---

@app.get("/grades")
async def get_grades():
    default_grades = ["Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10"]
    if supabase:
        res = supabase.table("syllabus").select("grade").execute()
        unique_grades = sorted(list(set([row["grade"] for row in res.data])))
        # If Supabase has data, use it. Otherwise, fallback to default.
        if len(unique_grades) > 0:
            return {"grades": unique_grades}
    return {"grades": default_grades}

@app.get("/subjects")
async def get_subjects(grade: str = Query(...)):
    default_subjects = ["Science", "Social Studies"]
    if supabase:
        res = supabase.table("syllabus").select("subject").eq("grade", grade).execute()
        unique_subjects = sorted(list(set([row["subject"] for row in res.data])))
        if len(unique_subjects) > 0:
            return {"subjects": unique_subjects}
    return {"subjects": default_subjects}

@app.get("/chapters")
async def get_chapters(grade: str = Query(...), subject: str = Query(...)):
    # Fallback to a generic list if Supabase isn't populated for this subject yet
    default_chapters = ["Chapter 1", "Chapter 2", "Chapter 3", "Chapter 4", "Chapter 5"]
    if supabase:
        res = supabase.table("syllabus").select("chapter_name").eq("grade", grade).eq("subject", subject).execute()
        unique_chapters = sorted(list(set([row["chapter_name"] for row in res.data])))
        if len(unique_chapters) > 0:
            return {"subject": subject, "chapters": unique_chapters}
    return {"subject": subject, "chapters": default_chapters}

@app.get("/level-test")
async def get_level_test(subject: str = Query(...)):
    if not supabase: return {"subject": subject, "questions": []}
    res = supabase.table("calibration_questions").select("*").eq("subject", subject).execute()
    if not res.data:
        return JSONResponse(status_code=404, content={"error": "No calibration questions found."})
    return {"subject": subject, "questions": res.data}

@app.post("/calculate-level")
async def calculate_level(data: LevelAnswers):
    if not data.answers:
        return {"level": "Intermediate", "median_score": 3}
    med = statistics.median(data.answers)
    if med <= 2: return {"level": "Beginner", "median_score": med}
    elif med <= 3: return {"level": "Intermediate", "median_score": med}
    return {"level": "Advanced", "median_score": med}

# --- RESTORED SESSION STATS ---
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

# --- AI CORE ENDPOINT ---

@app.get("/ask")
async def ask_assistant(
    user_query: str = Query(...), 
    student_level: str = Query("Intermediate"),
    subject: str = Query(...),   
    chapter: str = Query(...)    
):
    if not collection:
        return JSONResponse(status_code=500, content={"error": "Vector DB not initialized."})
    try:
        ai_data = get_prism_content_from_db(user_query, student_level, subject, chapter, collection)
        return JSONResponse(content=ai_data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- STATIC FILES ---

STATIC_DIR = "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("templates", "index.html"))
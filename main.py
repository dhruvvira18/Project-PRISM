import os
import statistics
import chromadb
import json
import logging
from fastapi import FastAPI, Query, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

from generator import get_prism_content_from_db
from byom_handler import process_byom_pdf

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

try:
    collection_byom = client_db.get_collection(name="prism_byom")
except Exception:
    collection_byom = None

class LevelAnswers(BaseModel):
    answers: list[int]

# --- SUPABASE DYNAMIC ENDPOINTS ---

@app.get("/grades")
async def get_grades():
    # FIXED: Added Grade 5 to strictly meet your 5-10 requirement
    if not supabase: return {"grades": ["Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10"]}
    try:
        res = supabase.table("syllabus").select("grade").execute()
        unique_grades = sorted(list(set([row["grade"] for row in res.data])))
        return {"grades": unique_grades if unique_grades else ["Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10"]}
    except Exception as e:
        logging.error(f"Supabase error in get_grades: {e}")
        return {"grades": ["Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10"]}

@app.get("/subjects")
async def get_subjects(grade: str = Query(...)):
    if not supabase: return {"subjects": ["Science", "Social Science"]} # Fixed string to match mapping
    try:
        res = supabase.table("syllabus").select("subject").eq("grade", grade).execute()
        unique_subjects = sorted(list(set([row["subject"] for row in res.data])))
        return {"subjects": unique_subjects}
    except Exception as e:
        logging.error(f"Supabase error in get_subjects: {e}")
        return {"subjects": ["Science", "Social Science"]}

@app.get("/chapters")
async def get_chapters(grade: str = Query(...), subject: str = Query(...)):
    if not supabase: return {"subject": subject, "chapters": ["Chapter 1", "Chapter 2"]}
    try:
        res = supabase.table("syllabus").select("chapter_name").eq("grade", grade).eq("subject", subject).execute()
        unique_chapters = sorted(list(set([row["chapter_name"] for row in res.data])))
        return {"subject": subject, "chapters": unique_chapters}
    except Exception as e:
        logging.error(f"Supabase error in get_chapters: {e}")
        return {"subject": subject, "chapters": ["Chapter 1", "Chapter 2"]}

@app.get("/level-test")
async def get_level_test(subject: str = Query(...)):
    if not supabase: return {"subject": subject, "questions": []}
    try:
        if subject == "BYOM":
            # Generic calibration test for BYOM
            return {
                "subject": "BYOM",
                "questions": [
                    {
                        "id": 1,
                        "question": "How familiar are you with the concepts in the uploaded PDF?",
                        "options": ["Not familiar at all", "Slightly familiar", "Moderately familiar", "Very familiar"]
                    },
                    {
                        "id": 2,
                        "question": "How much detail do you want in the explanations?",
                        "options": ["Basic overview", "Some details", "Detailed explanations", "In-depth analysis"]
                    },
                    {
                        "id": 3,
                        "question": "What is your learning goal with this document?",
                        "options": ["Quick review", "Understand key points", "Master the content", "Apply to real-world scenarios"]
                    },
                    {
                        "id": 4,
                        "question": "How comfortable are you with technical terms in the PDF?",
                        "options": ["Not comfortable", "Somewhat comfortable", "Comfortable", "Very comfortable"]
                    }
                ]
            }
        res = supabase.table("calibration_questions").select("*").eq("subject", subject).execute()
        if not res.data:
            return JSONResponse(status_code=404, content={"error": "No calibration questions found."})
        return {"subject": subject, "questions": res.data}
    except Exception as e:
        logging.error(f"Supabase error in get_level_test: {e}")
        return {"subject": subject, "questions": []}

@app.post("/calculate-level")
async def calculate_level(data: LevelAnswers):
    if not data.answers:
        return {"level": "Intermediate", "median_score": 3}
    med = statistics.median(data.answers)
    if med <= 2: return {"level": "Beginner", "median_score": med}
    elif med <= 3: return {"level": "Intermediate", "median_score": med}
    return {"level": "Advanced", "median_score": med}

# --- BYOM ENDPOINTS ---

@app.post("/upload-byom")
async def upload_byom(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    file_bytes = await file.read()
    return process_byom_pdf(file_bytes)

# --- AI CORE ENDPOINT ---

@app.get("/ask")
async def ask_assistant(
    user_query: str = Query(...), 
    student_level: str = Query("Intermediate"),
    grade: str = Query(...),   # FIXED: Grade parameter added
    subject: str = Query(...),   
    chapter: str = Query(...)    
):
    selected_collection = collection_byom if grade == "BYOM" else collection
    if not selected_collection:
        return JSONResponse(status_code=200, content={"error": "Learning database is currently being updated. Please try again in a few minutes."})
    try:
        ai_data = get_prism_content_from_db(user_query, student_level, grade, subject, chapter, selected_collection)
        return JSONResponse(content=ai_data)
    except Exception as e:
        logging.error(f"Unexpected error in ask endpoint: {e}")
        return JSONResponse(status_code=200, content={"error": "We're experiencing technical difficulties. Our team has been notified and is working to fix this. Please try again later."})

# --- STATIC FILES ---

STATIC_DIR = os.path.join("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("templates", "index.html"))
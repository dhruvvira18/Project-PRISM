import os
import statistics
import chromadb
import json
import logging
import bcrypt
from fastapi import FastAPI, Query, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

from byom_handler import process_byom_pdf
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

try:
    collection_byom = client_db.get_collection(name="prism_byom")
except Exception:
    try:
        collection_byom = client_db.create_collection(name="prism_byom")
    except Exception:
        collection_byom = None

class LevelAnswers(BaseModel):
    answers: list[int]

# --- AUTHENTICATION MODELS ---
class AuthEmailCheck(BaseModel):
    email: str

class AuthSignup(BaseModel):
    email: str
    password: str
    name: str

class AuthLogin(BaseModel):
    email: str
    password: str

class AuthUpdateLevel(BaseModel):
    user_id: str
    subject: str
    level: str

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/auth/check-email")
async def check_email(data: AuthEmailCheck):
    if not supabase:
        return {"exists": False}

    res = supabase.table("users").select("id").eq("email", data.email).execute()
    exists = len(res.data) > 0
    return {"exists": exists}

@app.post("/auth/signup")
async def signup(data: AuthSignup):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Check if user already exists
    res = supabase.table("users").select("id").eq("email", data.email).execute()
    if len(res.data) > 0:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(data.password.encode('utf-8'), salt).decode('utf-8')

    # Insert new user with 'Pending' subject levels so they take the calibration test
    new_user = {
        "email": data.email,
        "password_hash": hashed,
        "science_level": "Pending",
        "social_science_level": "Pending",
        "total_points": 0,
        "current_streak": 0
    }

    res = supabase.table("users").insert(new_user).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to create user")

    user = res.data[0]
    return {
        "id": user["id"],
        "email": user["email"],
        "science_level": user["science_level"],
        "social_science_level": user["social_science_level"]
    }

@app.post("/auth/login")
async def login(data: AuthLogin):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    res = supabase.table("users").select("*").eq("email", data.email).execute()
    if len(res.data) == 0:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = res.data[0]
    hashed_password = user["password_hash"]

    if not bcrypt.checkpw(data.password.encode('utf-8'), hashed_password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "id": user["id"],
        "email": user["email"],
        "science_level": user.get("science_level") or "Pending",
        "social_science_level": user.get("social_science_level") or "Pending"
    }

@app.post("/auth/update-level")
async def update_level(data: AuthUpdateLevel):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    column_name = "science_level" if data.subject.lower() == "science" else "social_science_level"

    res = supabase.table("users").update({column_name: data.level}).eq("id", data.user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found or update failed")

    return {"success": True, column_name: res.data[0][column_name]}

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
    # Try reading from knowledge_base/<grade>/<subject>/mapping.json first
    grade_folder = grade.lower().replace(" ", "")
    subject_folder = subject.lower().replace(" ", "_")
    mapping_path = os.path.join("knowledge_base", grade_folder, subject_folder, "mapping.json")

    if os.path.exists(mapping_path):
        try:
            with open(mapping_path, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            chapters = [data["name"] for data in mapping.values()]
            if chapters:
                return {"subject": subject, "chapters": chapters}
        except Exception as e:
            logging.error(f"Error reading mapping.json: {e}")

    # Fallback to a generic list if Supabase isn't populated and mapping is missing
    default_chapters = ["Chapter 1", "Chapter 2", "Chapter 3", "Chapter 4", "Chapter 5"]
    if supabase:
        res = supabase.table("syllabus").select("chapter_name").eq("grade", grade).eq("subject", subject).execute()
        unique_chapters = sorted(list(set([row["chapter_name"] for row in res.data])))
        if len(unique_chapters) > 0:
            return {"subject": subject, "chapters": unique_chapters}
    return {"subject": subject, "chapters": default_chapters}

@app.get("/level-test")
async def get_level_test(subject: str = Query(...)):
    if not supabase:
        return {"subject": subject, "questions": []}

    res = supabase.table("calibration_questions").select("*").eq("subject", subject).execute()

    if not res.data:
        return JSONResponse(status_code=404, content={"error": "No calibration questions found."})

    return {"subject": subject, "questions": res.data}

@app.post("/calculate-level")
async def calculate_level(data: LevelAnswers):
    if not data.answers:
        return {"level": "Intermediate", "average_score": 2}

    # Calculate average of correctness values
    # Lower value = more correct. e.g. 1 = Advanced, 4 = Beginner
    avg = sum(data.answers) / len(data.answers)

    # 1.0 to ~1.8 -> Advanced
    # ~1.8 to ~2.6 -> Intermediate
    # ~2.6 to 4.0 -> Beginner

    if avg <= 1.8:
        return {"level": "Advanced", "average_score": avg}
    elif avg <= 2.6:
        return {"level": "Intermediate", "average_score": avg}
    return {"level": "Beginner", "average_score": avg}

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
    chapter: str = Query(...),
    grade: str = Query(None),
):
    active_collection = collection
    bypass_metadata = False
    if grade and grade.upper() == "BYOM":
        active_collection = collection_byom
        bypass_metadata = True
    elif subject.upper() == "BYOM":
        active_collection = collection_byom
        bypass_metadata = True

    if not active_collection:
        return JSONResponse(status_code=500, content={"error": "Vector DB not initialized."})

    try:
        ai_data = get_prism_content_from_db(
            user_query,
            student_level,
            subject,
            chapter,
            active_collection,
            bypass_metadata=bypass_metadata,
        )
        return JSONResponse(content=ai_data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/upload-byom")
async def upload_byom(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for BYOM uploads.")
    try:
        file_bytes = await file.read()
        chunk_count = process_byom_pdf(file_bytes)
        return {"message": "BYOM document uploaded successfully.", "chunks": chunk_count}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"BYOM upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process BYOM PDF. Please try again.")

# --- STATIC FILES ---

STATIC_DIR = "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("templates", "index.html"))

@app.get("/login")
async def read_login():
    return FileResponse(os.path.join("templates", "login.html"))
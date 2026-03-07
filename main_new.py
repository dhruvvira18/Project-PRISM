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

# --- NEW GRADE DATABASE ---
GRADE_SUBJECT_DB = {
    "Grade 5": ["Science", "Social Studies"],
    "Grade 6": ["Science", "Social Studies"],
    "Grade 7": ["Science", "Social Studies"]
}

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
    return {"grades": list(GRADE_SUBJECT_DB.keys())}

@app.get("/subjects")
async def get_subjects(grade: str = Query(...)):
    subjects = GRADE_SUBJECT_DB.get(grade, [])
    if not subjects:
        return JSONResponse(status_code=404, content={"error": "Grade not found."})
    return {"subjects": subjects}

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


@app.get("/")
async def read_index():
    return FileResponse('Project-PRISM\static\index_new.html')

@app.get("/ask")
async def ask_assistant(user_query: str = Query(...), student_level: str = Query("Intermediate")):
    if not collection:
        return JSONResponse(status_code=500, content={"title": "Error", "knowledge_cards": ["Database not initialized."]})

    try:
        results = collection.query(query_texts=[user_query], n_results=2)
        context = " ".join(results['documents'][0]) if results['documents'] else "No context found."

        prompt = f"""
        ROLE: Grade 6 ADHD Study Mentor.
        STUDENT_LEVEL: {student_level}
        CONTEXT: {context}
        QUERY: {user_query}
        
        RULES: 
        1. Break explanations down into small knowledge cards (40-80 words max per card).
        2. Use simple, engaging language. NO Bionic Reading. Bold **Full Keywords**.
        3. Provide a simple analogy, a multiple-choice quiz, and key_points ONLY for the final revision card.
        4. Adjust complexity according to the STUDENT_LEVEL.
        5. VISUAL BLUEPRINT: If the topic benefits from a diagram, generate a "visual" block.
           - Canvas size is 450x450. 
           - Objects can only be "rect", "circle", or "line". 
           - LABELS MUST BE EXTREMELY SHORT (1-3 words max!). Do not use long sentences.
           - For rects, ALWAYS use width >= 140 and height >= 50.
           - CRITICAL SPACING RULE: If stacking boxes vertically, leave at least 60 pixels of empty space between them! (e.g., y=20, y=130, y=240). DO NOT squish them.
           - Arrows need from [x,y], to [x,y]. 
           - EVERY object and arrow MUST have a unique "id" (string) for animation.
           - "animation_steps" is an ordered list of these IDs to show them step-by-step.
           - If no diagram is needed, return "visual": null.

        RETURN ONLY JSON:
        {{
          "title": "Topic Name",
          "knowledge_cards": ["Chunk 1...", "Chunk 2..."],
          "visual": {{
            "type": "flow_diagram",
            "objects": [
              {{"id":"box1","shape":"rect","x":155,"y":20,"width":140,"height":50,"label":"Observe"}},
              {{"id":"box2","shape":"rect","x":155,"y":130,"width":140,"height":50,"label":"Hypothesis"}}
            ],
            "arrows": [
              {{"id":"arrow1","label":"leads to","from":[225,70],"to":[225,125]}}
            ],
            "animation_steps": [{{"show":"box1"}}, {{"show":"arrow1"}}, {{"show":"box2"}}]
          }},
          "key_points": ["Point 1", "Point 2"],
          "analogy": "Metaphor here",
          "breadcrumb": "Grade 6 > Subject",
          "quiz": {{
            "question": "A clear question based on the text.",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
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
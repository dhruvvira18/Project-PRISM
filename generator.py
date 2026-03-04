import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_prism_content(grade: str, subject: str, chapter_num: str, topic: str):
    # 1. Path Construction
    folder_name = subject.lower().replace(" ", "_")
    base_path = os.path.join("knowledge_base", f"grade{grade}", folder_name)
    mapping_path = os.path.join(base_path, "mapping.json")

    # 2. Map Chapter Number to Filename
    try:
        with open(mapping_path, 'r') as f:
            mapping = json.load(f)
        
        chapter_info = mapping.get(chapter_num)
        if not chapter_info:
            return {"error": f"Chapter {chapter_num} not found in index."}
        
        filename = chapter_info.get("file")
        pdf_full_path = os.path.join(base_path, filename)
    except FileNotFoundError:
        return {"error": "Mapping file missing for this subject/grade."}

    # 3. Upload PDF to Gemini
    print(f"Reading grounded context: {chapter_info['name']} ({filename})...")
    
    # Use positional argument for the file path
    textbook_file = client.files.upload(file=pdf_full_path)

    # 4. Prompt with PDF Context
    system_prompt = (
        "You are an ADHD educational expert. Use ONLY the provided PDF to explain. "
        "If the topic is not in the PDF, say 'Information not found in textbook.' "
        "Output ONLY a raw JSON object with 'simplified_text' as a LIST of 3 short strings."
    )
    
    user_input = f"Using the provided textbook, explain the concept of '{topic}' for a Grade {grade} student."

    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=[textbook_file, user_input],
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json"
        }
    )
    
    # Cleaning Markdown if necessary
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
        
    return json.loads(raw_text)
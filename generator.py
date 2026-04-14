import os
import json
import logging
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client_ai = genai.Client(api_key=API_KEY)
print("API KEY BEING USED:", os.getenv("GEMINI_API_KEY"))

def get_prism_content_from_db(user_query: str, student_level: str, collection):
    """
    Queries ChromaDB for context, then generates ADHD-friendly content using Gemini.
    """
    if not collection:
        raise ValueError("Database collection is not initialized. Run ingest.py.")

    # 1. Retrieve Context from Vector DB
    try:
        results = collection.query(query_texts=[user_query], n_results=2)
        context = " ".join(results['documents'][0]) if results['documents'] else "No specific textbook context found."
    except Exception as e:
        logging.error(f"ChromaDB Query Error: {e}")
        context = "Error retrieving context."

    # 2. Build the ADHD-Optimized Prompt
    prompt = f"""
    ROLE: Grade 6-10 ADHD Study Mentor (DOPAMINE-OPTIMIZED).
    STUDENT_LEVEL: {student_level}
    CONTEXT: {context}
    QUERY: {user_query}
    
    CRITICAL ADHD RULES FOR MAXIMUM EFFECTIVENESS:
    1. **CONTENT LIMIT**: flashcard_content = MAXIMUM 2 SENTENCES. ONE core concept only.
    2. **DOPAMINE HOOK**: Start with something surprising, fun, or relatable to grab attention.
    3. **Bold ONLY key term** (max 5 words per bold): **Chemical Reaction** not long phrases.
    4. **Analogy**: Use EVERYDAY objects (phone, pizza, skateboard) - NO technical jargon.
    5. **Quiz Calibration**: Beginner should feel 70% success (confidence), Intermediate 60%, Advanced 50%.
    6. **Visuals (CRITICAL FOR UNDERSTANDING)**:
       - ALWAYS provide visual if concept is sequential or has steps.
       - FLOWCHART MUST BE VERTICAL (top-down flow only, never horizontal).
       - ALWAYS include ARROWS connecting boxes/steps (arrows show the flow direction).
       - Arrow format: {{"id":"arrow1","label":"then","from":[225,70],"to":[225,100]}}
       - Labels on arrows: "then", "creates", "causes", "leads to", "results in"
       - Keep labels 1-3 words max on boxes and arrows.
    7. **Flashcards**: Use a maximum of 3 bullet points per flashcard. Max 3 bullet points per card.
    8. **Key Points**: Max 3, each ONE sentence, highly memorable.

    RETURN ONLY VALID JSON:
    {{
      "title": "SHORT TITLE (2-3 words max)",
      "flashcards": [
        {{
          "title": "Flashcard 1",
          "bullet_points": ["Point 1", "Point 2", "Point 3"]
        }}
      ],
      "dopamine_hook": "Fun fact, surprising connection, or real-world relevance",
      "visual": {{
        "type": "flow_diagram",
        "objects": [
          {{"id":"box1","shape":"rect","x":155,"y":20,"width":140,"height":50,"label":"Step 1"}}
        ],
        "arrows": [
          {{"id":"arrow1","label":"then","from":[225,70],"to":[225,100]}}
        ],
        "animation_steps": [{{"show":"box1"}}, {{"show":"arrow1"}}]
      }},
      "key_points": ["Memorable point 1", "Memorable point 2"],
      "analogy": "Real-world everyday object comparison",
      "quiz": {{
        "question": "Clear question (simple language).",
        "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
        "correct": "Exact string of correct option",
        "explanation": "Why correct + growth mindset encouragement"
      }}
    }}"""

    # 3. Call Gemini
    response = client_ai.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )

    # 4. Clean and Parse JSON
    text_response = response.text.strip()
    if "```json" in text_response:
        text_response = text_response.split("```json")[1].split("```")[0].strip()
    elif "```" in text_response:
        text_response = text_response.split("```")[1].split("```")[0].strip()

    print("Raw Gemini Response:", text_response)  # Debugging line
    
    return json.loads(text_response)
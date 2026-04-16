import os
import json
import logging
from google import genai
from google.genai import types 
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client_ai = genai.Client(api_key=API_KEY)

# FIXED: Added `grade` to signature
def get_prism_content_from_db(user_query: str, student_level: str, grade: str, subject: str, chapter: str, collection):
    """
    Queries ChromaDB for context, enforces strict syllabus bounds, and generates UI-friendly content.
    """
    if not collection:
        raise ValueError("Database collection is not initialized. Run ingest.py.")

    # 1. Format frontend strings to match ChromaDB metadata from ingest.py
    # "Grade 6" -> "grade6"
    formatted_grade = grade.lower().replace(" ", "")
    # "Social Science" -> "social_science"
    formatted_subject = subject.lower().replace(" ", "_")
    chapter = chapter.strip()
    normalized_chapter = " ".join(chapter.lower().split())

    redirect_response = {
        "title": "Let's Stay on Track!",
        "flashcards": [{
            "title": "Out of Bounds",
            "bullet_points": [
                f"That question isn't covered in **{chapter}**.",
                f"We are currently focusing our brains on {subject}.",
                "Try asking something about our current topic!"
            ]
        }],
        "dopamine_hook": "Focused brains learn faster! ✨",
        "visual": {"type": "flow_diagram", "objects": [], "arrows": [], "animation_steps": []},
        "key_points": ["Stay curious", "Focus on the current chapter"],
        "analogy": "Learning is like a map — you have to explore one zone before unlocking the next.",
        "quiz": {
            "question": "Which chapter are we studying right now?",
            "options": [f"A. {chapter}", "B. A random topic", "C. Something else", "D. I forgot"],
            "correct": f"A. {chapter}",
            "explanation": "Correct! Staying focused helps your brain learn faster."
        }
    }

    # 2. Retrieve Context from Vector DB (Strict Filtering with Graceful Degradation)
    try:
        # First attempt: Exact match on grade, subject, and chapter
        results = collection.query(
            query_texts=[user_query], 
            n_results=5,  # Increased to 5 for adequate context
            where={
                "$and": [
                    {"grade": {"$eq": formatted_grade}},
                    {"subject": {"$eq": formatted_subject}},
                    {"chapter_name": {"$eq": chapter}}
                ]
            }
        )

        # If no results, try normalized chapter name match
        if not results['documents'] or not results['documents'][0]:
            logging.info(f"No exact chapter match found for '{chapter}', trying normalized chapter lookup.")
            results = collection.query(
                query_texts=[user_query], 
                n_results=5,
                where={
                    "$and": [
                        {"grade": {"$eq": formatted_grade}},
                        {"subject": {"$eq": formatted_subject}},
                        {"chapter_name_normalized": {"$eq": normalized_chapter}}
                    ]
                }
            )

        # If still no results, fallback to grade and subject only
        if not results['documents'] or not results['documents'][0]:
            logging.info(f"No chapter-level match found, falling back to grade and subject for Grade: {formatted_grade}, Subject: {formatted_subject}")
            results = collection.query(
                query_texts=[user_query], 
                n_results=5,
                where={
                    "$and": [
                        {"grade": {"$eq": formatted_grade}},
                        {"subject": {"$eq": formatted_subject}}
                    ]
                }
            )

        # Final fallback: grade-only retrieval if subject metadata is inconsistent
        if not results['documents'] or not results['documents'][0]:
            logging.info(f"No grade+subject results found, falling back to grade only for Grade: {formatted_grade}")
            results = collection.query(
                query_texts=[user_query], 
                n_results=5,
                where={"grade": {"$eq": formatted_grade}}
            )

        if not results['documents'] or not results['documents'][0]:
            logging.warning(f"No context found in DB after all fallbacks for Grade: {formatted_grade}, Subject: {formatted_subject}")
            return redirect_response

        context = " ".join(results['documents'][0])
    except Exception as e:
        logging.error(f"ChromaDB Query Error: {e}")
        return redirect_response 

    # 3. Build the STRICT Guardrail Prompt
    prompt = f"""
    You are a strict Retrieval-Augmented Generation (RAG) AI for an Educational platform.
    You operate under a ZERO-HALLUCINATION policy. Your primary directive is factual accuracy based strictly on the provided context.

    [CONTEXT BEGIN]
    {context}
    [CONTEXT END]

    [USER REQUEST]
    STUDENT_LEVEL: {student_level}
    CURRENT_GRADE: {grade}
    CURRENT_SUBJECT: {subject}
    CURRENT_CHAPTER: {chapter}
    QUERY: {user_query}

    [STRICT SYLLABUS GUARDRAILS]
    1. Evaluate if the CONTEXT contains enough information to answer the user's QUERY.
    2. If the CONTEXT does NOT contain the answer, you MUST output EXACTLY the following JSON string and stop immediately:
    {json.dumps(redirect_response)}
    3. You may use your internal knowledge ONLY to define basic terms that are fundamentally linked to the retrieved context (e.g., if the context discusses "States of Water", you may define "water" as H2O). Do NOT use internal knowledge for any other purposes. Base all substantive answers strictly on the CONTEXT.

    [FORMATTING RULES]
    If and ONLY if the QUERY can be answered by the CONTEXT, format your response strictly as valid JSON using the following rules:
    1. **CONTENT LIMIT**: flashcard_content = MAXIMUM 2 SENTENCES. ONE core concept only.
    2. **DOPAMINE HOOK**: Start with something surprising or relatable to grab attention.
    3. **Bold ONLY key term** (max 5 words per bold).
    4. **Analogy**: Use EVERYDAY objects (phone, pizza, skateboard) - NO technical jargon.
    5. **Visuals**: Provide visual flowcharts if the concept is sequential.
    6. **Flashcards**: Max 3 bullet points per card. Max 3 cards total.
    7. **Key Points**: Max 3, each ONE sentence, highly memorable.

    [REQUIRED JSON SCHEMA]
    {{
      "title": "SHORT TITLE",
      "flashcards": [ {{"title": "Flashcard 1", "bullet_points": ["Point 1"]}} ],
      "dopamine_hook": "Fun fact...",
      "visual": {{ "type": "flow_diagram", "objects": [], "arrows": [], "animation_steps": [] }},
      "key_points": ["Memorable point 1"],
      "analogy": "Analogy...",
      "quiz": {{
        "question": "Clear question based ON THE CONTEXT.",
        "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
        "correct": "Exact string of correct option",
        "explanation": "Why correct"
      }}
    }}
    """

    try:
        response = client_ai.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json" 
            )
        )
        text_response = response.text.strip()
        
        if text_response.startswith("```json"):
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif text_response.startswith("```"):
            text_response = text_response.split("```")[1].split("```")[0].strip()
            
        return json.loads(text_response)
    except Exception as e:
        logging.error(f"Gemini API or Parsing Error: {e}")
        return redirect_response
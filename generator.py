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
        "title": "Content Not Available",
        "flashcards": [{
            "title": "Chapter Context Missing",
            "bullet_points": [
                f"Context for **{chapter}** in {subject} (Grade {grade}) is not yet indexed.",
                "This chapter's content is being prepared for your learning journey.",
                "Try exploring other chapters or ask about different topics!"
            ]
        }],
        "dopamine_hook": "Great question! We're expanding our knowledge base. 🚀",
        "visual": {"type": "flow_diagram", "objects": [], "arrows": [], "animation_steps": []},
        "key_points": ["Content indexing in progress", "Explore available chapters"],
        "analogy": "It's like waiting for a new book chapter to be published — exciting things are coming!",
        "quiz": {
            "question": f"What grade are we currently exploring?",
            "options": ["A. Grade 6", "B. Grade 7", "C. Grade 8", "D. Grade 9"],
            "correct": "A. Grade 6",
            "explanation": "We're building comprehensive content for all grades. Stay tuned!"
        }
    }

    # 2. Retrieve Context from Vector DB (Strict Filtering with Graceful Degradation)
    try:
        if grade == "BYOM":
            # For BYOM, query without filters since metadata may vary
            logging.info(f"Querying BYOM ChromaDB for user_query: {user_query}")
            results = collection.query(query_texts=[user_query], n_results=5)
            logging.info(f"BYOM query results: {len(results['documents'][0]) if results['documents'] else 0} chunks")
        else:
            # First attempt: Exact match on grade, subject, and chapter
            logging.info(f"Querying ChromaDB: grade={formatted_grade}, subject={formatted_subject}, chapter={chapter}")
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
            logging.info(f"Exact match results: {len(results['documents'][0]) if results['documents'] else 0} chunks")

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
                logging.info(f"Normalized chapter results: {len(results['documents'][0]) if results['documents'] else 0} chunks")

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
                logging.info(f"Grade+subject fallback results: {len(results['documents'][0]) if results['documents'] else 0} chunks")

            # Final fallback: grade-only retrieval if subject metadata is inconsistent
            if not results['documents'] or not results['documents'][0]:
                logging.info(f"No grade+subject results found, falling back to grade only for Grade: {formatted_grade}")
                results = collection.query(
                    query_texts=[user_query], 
                    n_results=5,
                    where={"grade": {"$eq": formatted_grade}}
                )
                logging.info(f"Grade-only fallback results: {len(results['documents'][0]) if results['documents'] else 0} chunks")

        # Validation: Ensure we have actual content
        if not results['documents'] or not results['documents'][0] or not any(chunk.strip() for chunk in results['documents'][0]):
            logging.warning(f"No valid context chunks found after all fallbacks for query: '{user_query}' in Grade: {formatted_grade}, Subject: {formatted_subject}, Chapter: {chapter}")
            return redirect_response

        context = " ".join(results['documents'][0])
        
        # Additional validation: Ensure context is not empty after joining
        if not context.strip():
            logging.warning(f"Context is empty after joining chunks for query: '{user_query}'")
            return redirect_response
            
        logging.info(f"Final context length: {len(context)} characters")
        
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
    5. **Visuals**: Always provide a basic visual diagram (e.g., simple flowchart or concept map) to illustrate the concept.
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
import os
import json
import logging
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.getenv("GEMINI_API_KEY")
client_ai = genai.Client(api_key=API_KEY)
print(API_KEY)

def get_prism_content_from_db(user_query: str, student_level: str, subject: str, chapter: str, collection, bypass_metadata: bool = False):
    """
    Queries ChromaDB for context, enforces syllabus bounds, and generates ADHD-friendly content.
    """
    if not collection:
        raise ValueError("Database collection is not initialized. Run ingest.py.")

    # --- RULE: PRE-DEFINED ADHD REDIRECT ---
    redirect_response = {
        "title": "Let's Stay on Track!",
        "flashcards": [
            {
                "title": "Oops!",
                "bullet_points": [
                    f"That question isn't part of the **{chapter}** chapter.",
                    f"We are currently focusing our brains on {subject}.",
                    "Try asking something about our current topic!"
                ]
            }
        ],
        "dopamine_hook": "Focused brains learn faster! ✨",
        "visual": {"type": "flow_diagram", "objects": [], "arrows": [], "animation_steps": []},
        "key_points": ["Stay curious", "Focus on one concept at a time"],
        "analogy": "Learning is like leveling up in a game — one level at a time.",
        "quiz": {
            "question": "Which chapter are we studying right now?",
            "options": [
                f"A. {chapter}",
                "B. A random topic",
                "C. A different subject",
                "D. Something else"
            ],
            "correct": f"A. {chapter}",
            "explanation": "Correct! Staying focused helps your brain learn faster."
        }
    }

    # 1. Retrieve Context from Vector DB
    try:
        if bypass_metadata:
            results = collection.query(query_texts=[user_query], n_results=2)
        else:
            results = collection.query(
                query_texts=[user_query],
                n_results=2,
                where={
                    "$and": [
                        {"subject": {"$eq": subject.lower().replace(" ", "_")}},
                        {"chapter_name": {"$eq": chapter}}
                    ]
                }
            )

        # Guardrail: If no context is found, block the AI and redirect the user
        if not results["documents"] or not results["documents"][0]:
            logging.info("No context found. Triggering ADHD redirect.")
            return redirect_response

        context = " ".join(results["documents"][0])
    except Exception as e:
        logging.error(f"ChromaDB Query Error: {e}")
        return redirect_response 

    # 2. Build the STRICT Guardrail Prompt with RESTORED VISUAL RULES
    prompt = f"""
    ROLE: Grade 6-10 ADHD Study Mentor (DOPAMINE-OPTIMIZED).
    STUDENT_LEVEL: {student_level}
    CURRENT_SUBJECT: {subject}
    CURRENT_CHAPTER: {chapter}
    CONTEXT: {context}
    QUERY: {user_query}
    
    STRICT SYLLABUS GUARDRAILS:
    - You MUST ONLY answer using the provided CONTEXT. 
    - Do NOT answer general knowledge questions.
    - Do NOT answer questions outside Science or Social Studies.
    - If the user QUERY is unrelated to the context, you MUST output EXACTLY the following JSON string and nothing else, then stop:
      {json.dumps(redirect_response)}

    CRITICAL ADHD RULES:
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

    # 3. Call Gemini (Wrapped in a Try/Except block for server resilience)
    try:
        response = client_ai.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
    except Exception as api_error:
        logging.error(f"Gemini API Down/Failed: {api_error}")
        return {
            "title": "Network Hiccup! 🛑",
            "flashcards": [
                {
                    "title": "AI Taking a Breather",
                    "bullet_points": [
                        "Our supercomputer brain (Gemini) is temporarily overloaded.",
                        "This is a server traffic jam, not your fault!",
                        "Take a deep breath, wait 5 seconds, and hit Ask again."
                    ]
                }
            ],
            "dopamine_hook": "Even supercomputers need to blink sometimes! 👀",
            "visual": {"type": "flow_diagram", "objects": [], "arrows": [], "animation_steps": []},
            "key_points": ["Wait 5 seconds", "Try your question again"],
            "analogy": "It's like when a YouTube video buffers. The internet just needs a second to catch up.",
            "quiz": None
        }

    # 4. Clean and Parse JSON (Also wrapped safely)
    try:
        text_response = response.text.strip()
        if "```json" in text_response:
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif "```" in text_response:
            text_response = text_response.split("```")[1].split("```")[0].strip()
        
        return json.loads(text_response)
    except Exception as parse_error:
        logging.error(f"Failed to parse Gemini output: {parse_error}\nRaw Text: {response.text}")
        return {
            "title": "Brain Misfire! ⚡",
            "flashcards": [{
                "title": "Formatting Glitch",
                "bullet_points": ["Gemini got too excited and forgot how to format its response.", "Try asking your question slightly differently!"]
            }],
            "dopamine_hook": "Sometimes our brains speak too fast for our mouths!",
            "visual": {"type": "flow_diagram", "objects": [], "arrows": [], "animation_steps": []},
            "key_points": ["Try rephrasing the question"],
            "analogy": "Like writing outside the lines in a coloring book.",
            "quiz": None
        }
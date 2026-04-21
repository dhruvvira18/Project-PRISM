import re

with open("main.py", "r") as f:
    content = f.read()

s1 = """class ChatEntry(BaseModel):
    user_id: str
    session_id: str
    subject: str
    chapter: str
    user_query: str
    ai_response: str"""
r1 = """class ChatEntry(BaseModel):
    user_id: str
    session_id: str
    subject: str
    chapter: str
    user_query: str
    ai_response: str
    concept_title: str | None = None
    content: str | None = None"""
content = content.replace(s1, r1)

s2 = """@app.post("/chat")
async def save_chat(data: ChatEntry):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    new_chat = {
        "user_id": data.user_id,
        "session_id": data.session_id,
        "subject": data.subject,
        "chapter": data.chapter,
        "user_query": data.user_query,
        "ai_response": data.ai_response,
        "is_helpful": True # Default
    }

    res = supabase.table("chat_history").insert(new_chat).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to save chat")

    return {"success": True, "chat_id": res.data[0]["id"]}"""
r2 = """@app.post("/chat")
async def save_chat(data: ChatEntry):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    new_chat = {
        "user_id": data.user_id,
        "session_id": data.session_id,
        "subject": data.subject,
        "chapter": data.chapter,
        "user_query": data.user_query,
        "ai_response": data.ai_response,
        "is_helpful": True # Default
    }

    res = supabase.table("chat_history").insert(new_chat).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail="Failed to save chat")

    if data.concept_title and data.content:
        new_flashcard = {
            "user_id": data.user_id,
            "concept_title": data.concept_title,
            "content": data.content
        }
        try:
            supabase.table("saved_flashcards").insert(new_flashcard).execute()
        except Exception as e:
            logging.error(f"Failed to save flashcard: {e}")

    return {"success": True, "chat_id": res.data[0]["id"]}"""
content = content.replace(s2, r2)

with open("main.py", "w") as f:
    f.write(content)
print("Done")

# PRISM Project Context & Architecture

## Tech Stack
* **Backend:** Python, FastAPI
* **AI Model:** Google GenAI SDK (Gemini 2.5 Flash / 1.5 Flash)
* **Vector Database:** ChromaDB (Persistent, local `./prism_db`)
* **Frontend:** HTML/CSS/JS (Bootstrap/Vanilla), Jinja2 Templates
* **Database/Auth:** Supabase (PostgreSQL)

## Core Directives for Jules
1.  **Strict Adherence:** Do not change the core architecture. We are using FastAPI and ChromaDB. Do not suggest switching to LangChain or other heavy frameworks.
2.  **RAG Integrity:** The system uses a RAG pipeline. A known bug is that Gemini is hallucinating instead of using the ChromaDB context. Always ensure prompt structures strictly bind the AI to the `context` variable.
3.  **Frontend Rules:** Do not use React or Vue. Stick to Vanilla JS and Jinja2 templating. Keep CSS aligned with the existing Sage/Cream color palette.
4.  **Supabase Integration:** Ensure all database calls to Supabase are asynchronous where possible to avoid blocking the FastAPI event loop.

## Testing the RAG Pipeline (CRITICAL TIME-SAVER)
Do NOT run the main `ingest.py` script. It processes over 100 PDFs and takes 2 hours. 
To test your fixes to the RAG pipeline in `generator.py` or `main.py`, please create a temporary script called `test_ingest.py` that only vectorizes a single hardcoded string (e.g., "The mitochondria is the powerhouse of the cell") into ChromaDB. Use this tiny test DB to verify that Gemini is reading from the `context` variable properly.
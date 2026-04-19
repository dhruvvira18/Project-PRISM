import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    res = supabase.table("syllabus").select("*").limit(1).execute()
    print("Columns:", res.data[0].keys() if res.data else "No data")
else:
    print("No Supabase credentials")

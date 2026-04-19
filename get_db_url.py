import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
if SUPABASE_URL:
    db_host = SUPABASE_URL.replace("https://", "db.").replace(".supabase.co", ".supabase.co")
    print(db_host)

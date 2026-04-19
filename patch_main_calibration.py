with open("main.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.startswith('@app.get("/level-test")'):
        skip = True
        new_lines.append('@app.get("/level-test")\n')
        new_lines.append('async def get_level_test():\n')
        new_lines.append('    if not supabase:\n')
        new_lines.append('        return {"questions": []}\n')
        new_lines.append('    res = supabase.table("calibration_questions").select("*").execute()\n')
        new_lines.append('    if not res.data:\n')
        new_lines.append('        return JSONResponse(status_code=404, content={"error": "No calibration questions found."})\n')
        new_lines.append('    return {"questions": res.data}\n\n')
        continue

    if line.startswith('@app.post("/calculate-level")'):
        skip = True
        new_lines.append('@app.post("/calculate-level")\n')
        new_lines.append('async def calculate_level(data: LevelAnswers):\n')
        new_lines.append('    if not data.answers:\n')
        new_lines.append('        return {"level": "Intermediate", "median_score": 3}\n')
        new_lines.append('    med = statistics.median(data.answers)\n')
        new_lines.append('    if med <= 1.5: return {"level": "Advanced", "median_score": med}\n')
        new_lines.append('    elif med <= 2.5: return {"level": "Intermediate", "median_score": med}\n')
        new_lines.append('    return {"level": "Beginner", "median_score": med}\n\n')
        continue

    if skip and line.startswith('# --- RESTORED SESSION STATS ---'):
        skip = False

    if not skip:
        new_lines.append(line)

with open("main.py", "w") as f:
    f.writelines(new_lines)

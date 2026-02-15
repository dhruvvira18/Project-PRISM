def get_prompt(level, subject, topic):

    common_rules = """
Rules:
- Use short sentences.
- Explain one idea at a time.
- Avoid unnecessary storytelling.
- Avoid jokes.
- Keep the explanation under 150 words.
"""

    if level == 1:
        return f"""
You are teaching an ADHD student from grade 5.

Subject: {subject}
Topic: {topic}

Explain the topic in very simple words.
Avoid scientific terms.
Explain like teaching a young student.

{common_rules}
"""

    elif level == 2:
        return f"""
You are teaching an ADHD student from grade 6–7.

Subject: {subject}
Topic: {topic}

Explain the topic using simple school-level language.
Keep explanations clear and structured.

{common_rules}
"""

    elif level == 3:
        return f"""
You are teaching an ADHD student from grade 8–9.

Subject: {subject}
Topic: {topic}

Explain the topic clearly using basic scientific terms.
Avoid long paragraphs.

{common_rules}
"""

    else:
        return f"""
You are teaching an ADHD student from grade 10.

Subject: {subject}
Topic: {topic}

Explain the topic clearly at textbook level,
but keep the explanation structured and easy to follow.

{common_rules}
"""

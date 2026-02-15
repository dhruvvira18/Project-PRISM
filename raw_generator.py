import ollama


def generate_raw_text(subject, topic):
    """
    Generates a raw, textbook-style explanation.
    This simulates unprocessed textbook content.
    """

    prompt = f"""
Write a textbook-style explanation for the topic "{topic}" from {subject}.

Requirements:
- Use formal academic language
- Do NOT simplify
- Write in paragraph form
- Assume this is from a school textbook
"""

    response = ollama.generate(
        model="phi3:mini",
        prompt=prompt
    )

    return response["response"]


def rewrite_text(subject, topic, text, level):
    level_rules = {
        1: "Use very simple words. Short sentences. Avoid scientific terms.",
        2: "Use simple school-level language. Explain clearly.",
        3: "Use basic scientific terms. Keep it structured.",
        4: "Use textbook-level language but keep it concise."
    }

    prompt = f"""
You are an AI tutor for an ADHD student.

Rewrite the content below.
ONLY output the rewritten explanation.
Do NOT include headings, instructions, or analysis.

Content:
{text}

Rules:
- {level_rules[level]}
- One core idea
- 40–60 words
- Clear and factual
- Do NOT add new examples unless asked
"""

    stream = ollama.generate(
        model="phi3:mini",
        prompt=prompt,
        stream=True
    )

    for chunk in stream:
        if "response" in chunk:
            yield chunk["response"]

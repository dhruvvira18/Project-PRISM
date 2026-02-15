def structure_text(text):
    sentences = [s.strip() for s in text.split(".") if s.strip()]

    if len(sentences) <= 1:
        return text

    structured = "\n".join(f"- {s}" for s in sentences)
    return structured

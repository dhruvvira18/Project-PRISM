import ollama
from focus_mode.prompts import get_prompt

def generate_focus_content_stream(subject, topic, level):
    prompt = get_prompt(level, subject, topic)

    print("\n--- Focus Mode Output ---\n")

    for chunk in ollama.generate(
        model='llama3.1:8b',
        prompt=prompt,
        stream=True
    ):
        if 'response' in chunk:
            print(chunk['response'], end='', flush=True)

    print("\n")  # final newline

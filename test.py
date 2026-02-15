import ollama

response = ollama.chat(
    model='llama3.1:8b',
    messages=[
        {
            'role': 'user',
            'content': 'Explain photosynthesis to a grade 6 student in simple words.'
        }
    ]
)

print(response['message']['content'])

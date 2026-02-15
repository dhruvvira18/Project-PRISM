from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

def summarize_text(text):
    summary = summarizer(
        text,
        max_length=180,
        min_length=120,
        do_sample=False
    )
    return summary[0]["summary_text"]

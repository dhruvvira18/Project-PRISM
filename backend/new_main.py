from focus_mode_new.assessment import conduct_language_assessment
from focus_mode_new.raw_generator import generate_raw_text, rewrite_text
from focus_mode_new.summarizer import summarize_text
from focus_mode_new.chunker import chunk_text
from focus_mode_new.simplifier import simplify_text
from focus_mode_new.structure import structure_text
from focus_mode_new.session import run_focus_session


def main():
    print("\n===== ADHD Focus Mode =====\n")

    subject = input("Enter subject (Biology / Physics / Chemistry / SST): ").strip()

    print("\n--- Language Preference Assessment ---")
    level = conduct_language_assessment(subject)
    print(f"\nAssigned Starting Level: {level}")

    topic = input("\nEnter topic you want to study: ").strip()

    # Pipeline dictionary (core Focus Mode flow)
    pipeline = {
        "raw": generate_raw_text,        # LLaMA raw explanation
        "summarize": summarize_text,     # Extractive summarization
        "chunk": chunk_text,             # Micro-card slicing
        "simplify": simplify_text,       # Lexical simplification
        "structure": structure_text,     # Bullet / list conversion
        "rewrite": rewrite_text          # Level-aware rewriting via LLaMA
    }

    # Start continuous Focus Mode session
    run_focus_session(subject, topic, level, pipeline)


if __name__ == "__main__":
    main()

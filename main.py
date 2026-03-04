from generator import get_prism_content
import os

def run_test():
    print("\nPRISM v2.0 | (RAG)")
    print("---------------------------------------")
    
    try:
        grade = input("Enter Grade (6-10): ")
        subject = input("Enter Subject (science/social_science): ")
        chapter = input("Enter Chapter Number: ")
        topic = input("Enter Topic to simplify: ")
        
        print("\nStep 1: Accessing textbook and refactoring...")
        data = get_prism_content(grade, subject, chapter, topic)
        
        if "error" in data:
            print(f"Notice: {data['error']}")
            return

        print("\n[FOCUS MODE: TEXT]")
        points = data.get('simplified_text', [])
        
        if isinstance(points, list):
            for point in points:
                print(f"- {point}")
        else:
            print(f"- {points}")

        print("\nSuccess: Content generated from source PDF.")

    except Exception as e:
        print(f"\n[System Error]: {e}")

if __name__ == "__main__":
    run_test()
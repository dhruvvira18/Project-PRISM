from focus_mode.assessment import conduct_assessment
from focus_mode.level_mapper import map_score_to_level
from focus_mode.generator import generate_focus_content_stream

subject = input("Enter subject (Biology/Physics/Chemistry/SST): ")
grade = int(input("Enter your grade (5–10): "))

score, total = conduct_assessment(subject, grade)
level = map_score_to_level(score, total)

print(f"\nScore: {score}/{total}")
print(f"Assigned Level: {level}")

topic = input("\nEnter topic you want to study: ")

generate_focus_content_stream(subject, topic, level)


def run_focus_session(subject, topic, level, pipeline):
    print("\n--- Focus Mode Started ---")
    print("Commands: simplify | next | exit\n")

    raw_text = pipeline["raw"](subject, topic)
    summary = pipeline["summarize"](raw_text)
    chunks = pipeline["chunk"](summary)

    current_level = level
    index = 0

    while index < len(chunks):
        base_text = chunks[index]

        # Apply lexical + structural preprocessing
        processed_text = pipeline["simplify"](base_text)
        processed_text = pipeline["structure"](processed_text)

        print("\n" + "=" * 50)
        print(f"--- Card {index + 1} (Level {current_level}) ---\n")

        # Stream rewritten content
        for token in pipeline["rewrite"](
            subject,
            topic,
            processed_text,
            current_level
        ):
            print(token, end="", flush=True)

        print("\n" + "=" * 50)

        user = input("\nYou: ").lower().strip()

        if user == "simplify":
            if current_level > 1:
                current_level -= 1
                print(f"(Simplifying → Level {current_level})")
            else:
                print("(Already at simplest level)")
            continue

        elif user == "next":
            index += 1
            continue

        elif user == "exit":
            break

        else:
            print("Type: simplify | next | exit")

    print("\n--- Focus Mode Ended ---")

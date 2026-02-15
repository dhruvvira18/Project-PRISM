SIMPLE_DICT = {
    "photosynthesis": "how plants make food",
    "osmosis": "movement of water in cells",
    "autotrophic": "makes its own food",
    "biochemical": "related to life chemistry",
    "respiration": "process of releasing energy",
    "chromosomes": "structures carrying genes"
}

def simplify_text(text):
    lowered = text.lower()

    for word, meaning in SIMPLE_DICT.items():
        if word in lowered:
            text = text.replace(
                word,
                f"{word} ({meaning})"
            )
    return text

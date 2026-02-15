# level_mapper.py

def map_score_to_level(score, total):
    if total == 0:
        return 1  # default safe level

    ratio = score / total

    if ratio <= 0.2:
        return 1   # Very basic
    elif ratio <= 0.4:
        return 2   # Basic
    elif ratio <= 0.7:
        return 3   # Moderate
    else:
        return 4   # Advanced

import re


IGNORE_WORDS = {
    "mr",
    "mrs",
    "ms",
    "dr",
    "md",
    "sir",
    "jr",
    "sr",
    "goud",
    "reddy",
    "kumar",
    "rao",
    "naidu"
}


def extract_display_name(full_name: str) -> str:

    if not full_name:
        return "User"

    cleaned = re.sub(
        r"[^\w\s]",
        "",
        full_name
    ).strip()

    parts = cleaned.split()

    filtered = []

    for part in parts:

        lower = part.lower()

        # skip initials
        if len(part) == 1:
            continue

        # skip ignored surnames/titles
        if lower in IGNORE_WORDS:
            continue

        filtered.append(part)

    if not filtered:
        return parts[0].title()

    # Prefer natural middle/calling name
    if len(filtered) >= 2:
        return filtered[1].title()

    return filtered[0].title()

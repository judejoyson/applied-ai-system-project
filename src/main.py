"""
Command line runner for the Music Recommender Simulation.

Run from the project root:  python -m src.main
"""

from typing import Dict, List, Tuple

from src.recommender import load_songs, recommend_songs

PROFILES: Dict[str, Dict] = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.90, "acousticness": 0.10},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.40, "acousticness": 0.75},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.92, "acousticness": 0.10},
}

# Edge cases designed to trick the scoring logic.
ADVERSARIAL_PROFILES: Dict[str, Dict] = {
    # "sad" is not a mood label in the catalog (it has "sorrowful" and "melancholy").
    "Conflict: High Energy + Sad": {"genre": "blues", "mood": "sad", "energy": 0.90},
    # Genre is heavy: does a genre match beat a total mismatch on everything else?
    "Conflict: Metal + Chill + Quiet": {
        "genre": "metal", "mood": "chill", "energy": 0.20, "acousticness": 0.90,
    },
    # Genre and mood that exist nowhere in the catalog: only numbers can score.
    "Unknown Genre (k-pop / happy)": {"genre": "k-pop", "mood": "happy", "energy": 0.80},
    # Maxed-out numbers: very loud and very acoustic at once.
    "Extreme: Energy 1.0 + Acoustic 1.0": {"energy": 1.0, "acousticness": 1.0},
}

WIDTH = 64


def format_recommendations(
    name: str, user_prefs: Dict, recommendations: List[Tuple[Dict, float, str]]
) -> str:
    prefs = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    lines = ["=" * WIDTH, f"Profile: {name}", f"  ({prefs})", "=" * WIDTH]
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        lines.append(f"{rank}. {song['title']} by {song['artist']}")
        lines.append(f"   Score: {score:.2f}")
        lines.append("   Why:")
        lines.extend(f"     - {reason}" for reason in explanation.split("; "))
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    for name, user_prefs in {**PROFILES, **ADVERSARIAL_PROFILES}.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print(format_recommendations(name, user_prefs, recommendations))


if __name__ == "__main__":
    main()

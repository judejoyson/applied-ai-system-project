"""
Command line runner for the Music Recommender Simulation.

Run from the project root:  python -m src.main
"""

from typing import Dict, List, Tuple

from src.recommender import load_songs, recommend_songs

PROFILES: Dict[str, Dict] = {
    "Pop / Happy (starter profile)": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.40, "acousticness": 0.75},
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

    for name, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print(format_recommendations(name, user_prefs, recommendations))


if __name__ == "__main__":
    main()

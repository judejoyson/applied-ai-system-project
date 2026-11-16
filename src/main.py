"""
Command line runner for the Music Recommender Simulation.

Run from the project root:  python -m src.main
"""

import argparse
from typing import Dict, List, Tuple

from src.rag import answer_query
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

# Natural-language queries that show off the RAG feature: the retriever finds
# relevant songs from data/songs.csv by meaning, not by exact genre/mood match,
# and the LLM answer is grounded only in what was retrieved.
DEMO_QUERIES: List[str] = [
    "I need something chill and acoustic for late-night studying",
    "I want a song that doesn't exist, like underwater polka",
]

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


def format_rag_result(result: Dict) -> str:
    lines = ["=" * WIDTH, f"Ask VibeMatch: {result['query']}", "=" * WIDTH]
    if result["retrieved"]:
        lines.append("Retrieved from catalog:")
        for song, score in result["retrieved"]:
            lines.append(
                f"  - {song['title']} by {song['artist']} "
                f"({song['genre']}, {song['mood']}, relevance {score:.2f})"
            )
    else:
        lines.append("Retrieved from catalog: (nothing relevant found)")
    lines.append("")
    source = "LLM-generated" if result["used_llm"] else "fallback, no LLM used"
    lines.append(f"Answer ({source}, confidence: {result['confidence']}):")
    lines.append(result["answer"])
    lines.append("")
    return "\n".join(lines)


def run_rag_query(query: str, songs: List[Dict]) -> None:
    result = answer_query(query, songs)
    print(format_rag_result(result))


def run_interactive(songs: List[Dict]) -> None:
    print("Ask VibeMatch about music in plain English. Type 'quit' to exit.\n")
    while True:
        try:
            query = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query or query.lower() in {"quit", "exit"}:
            break
        run_rag_query(query, songs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VibeMatch music recommender simulation")
    parser.add_argument(
        "--ask", type=str, default=None,
        help="Ask a natural-language question using the RAG pipeline and exit",
    )
    parser.add_argument(
        "--interactive", action="store_true",
        help="Start an interactive RAG question loop instead of running the demo",
    )
    parser.add_argument(
        "--skip-demo", action="store_true",
        help="When running with no other flags, skip the built-in demo output",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    if args.ask:
        run_rag_query(args.ask, songs)
        return

    if args.interactive:
        run_interactive(songs)
        return

    if args.skip_demo:
        return

    for name, user_prefs in {**PROFILES, **ADVERSARIAL_PROFILES}.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print(format_recommendations(name, user_prefs, recommendations))

    print("=" * WIDTH)
    print("RAG demo: natural-language questions answered from retrieved songs")
    print("=" * WIDTH)
    for query in DEMO_QUERIES:
        run_rag_query(query, songs)


if __name__ == "__main__":
    main()

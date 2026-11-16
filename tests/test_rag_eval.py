"""
Reliability evaluation for the RAG retriever, run against the real catalog
(data/songs.csv) instead of a hand-built test fixture.

The unit tests in test_rag.py use a tiny 3-song fixture and mock the LLM
call; they're good at proving guardrails fire correctly, but a small fixture
can accidentally avoid real-world failure modes. This file is a precision
check: for a fixed set of queries with known relevant songs (chosen by
reading data/songs.csv), does retrieve() actually surface them? It's the
regression test that would have caught the title-leakage bug described in
the README's Design Decisions (a query containing "night" out-ranking actual
chill/acoustic songs because of the word "Night" in a song title) before it
ever reached a user.
"""

from src.recommender import load_songs
from src.rag import retrieve

SONGS = load_songs("data/songs.csv")

# (query, set of titles where at least one must appear in the top-k results)
PRECISION_CASES = [
    (
        "chill acoustic lofi music for late-night studying",
        {"Midnight Coding", "Library Rain", "Spacewalk Thoughts", "Focus Flow"},
    ),
    (
        "upbeat happy pop song for a workout",
        {"Sunrise City", "Rooftop Lights", "Gym Hero"},
    ),
    (
        "heavy intense rock or metal song",
        {"Storm Runner", "Iron Cathedral"},
    ),
    (
        "sad slow acoustic song",
        {"Porch Light Blues", "Clockwork Sonata", "Dust Road Hymn"},
    ),
]

# Queries nothing in the 20-song catalog should satisfy: retrieve() must
# return nothing rather than force a low-quality match.
NO_MATCH_CASES = [
    "underwater polka about tax law",
    "zzqxv gibberish not a real request 48213",
]


def test_retrieval_precision_against_real_catalog():
    """For each known query, at least one expected song is in the top 5."""
    failures = []
    for query, expected_titles in PRECISION_CASES:
        results = retrieve(query, SONGS, k=5)
        retrieved_titles = {song["title"] for song, _ in results}
        if not (retrieved_titles & expected_titles):
            failures.append((query, expected_titles, retrieved_titles))

    assert not failures, (
        "Retrieval missed every expected song for these queries: "
        f"{failures}"
    )


def test_retrieval_abstains_on_unanswerable_queries():
    for query in NO_MATCH_CASES:
        results = retrieve(query, SONGS, k=5)
        assert results == [], f"Expected no matches for {query!r}, got {results}"


def test_retrieval_top_result_is_always_the_highest_score():
    """Sanity check that ranking is actually sorted, on real (not mocked) data."""
    for query, _ in PRECISION_CASES:
        results = retrieve(query, SONGS, k=5)
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)

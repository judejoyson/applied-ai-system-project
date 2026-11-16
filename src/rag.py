"""
Retrieval-Augmented Generation for the Music Recommender Simulation.

Given a free-text question ("something chill and acoustic for late-night
studying"), this module:

1. Retrieves the songs most relevant to the question from data/songs.csv
   using TF-IDF + cosine similarity over a text description built from each
   song's metadata (`retrieve`).
2. Hands only those retrieved songs to Claude as grounding context and asks
   it to recommend from that list and explain why, so the response is
   actually built from retrieved data rather than the model's own
   (unverifiable) music knowledge (`generate_grounded_answer`).

`answer_query` is the integration point main.py calls: it logs every step,
and if retrieval finds nothing relevant or no API key is configured, it
degrades to a plain listing of retrieved songs rather than failing or
inventing a song that isn't in the catalog.
"""

from __future__ import annotations

import logging
import math
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DEFAULT_MODEL = os.environ.get("VIBEMATCH_MODEL", "claude-haiku-5-5")
MAX_ANSWER_TOKENS = 500
# Below this cosine similarity, a song is treated as unrelated to the query
# rather than as a (misleading) weak match.
RELEVANCE_THRESHOLD = 0.05

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "rag.log"

logger = logging.getLogger("vibematch.rag")
if not logger.handlers:
    logger.setLevel(logging.DEBUG)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter("[rag] %(levelname)s: %(message)s"))
    logger.addHandler(console_handler)

_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Common English function words, stripped from both the indexed song text and
# incoming queries. Without this, a stray word like "not" (as in "I don't
# want anything too slow") can be the only overlapping token between a query
# and a song, and since out-of-vocabulary query words are silently
# zero-weighted (see TfidfIndex._query_vector), that one incidental stopword
# match can dominate the similarity score. Caught by
# tests/test_rag_eval.py::test_retrieval_abstains_on_unanswerable_queries.
_STOPWORDS = frozenset(
    """
    a an the is are was were be been being to of in on at for with and or but
    not no so do does did this that these those it its i you he she they we
    my your his her their our me him them us as if than then too very just
    really like please want need something some any what which who whom
    """.split()
)


def _tokenize(text: str) -> List[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


def _bucket(value: float, low_words: str, mid_words: str, high_words: str, low_cut: float, high_cut: float) -> str:
    if value < low_cut:
        return low_words
    if value > high_cut:
        return high_words
    return mid_words


def _song_to_retrieval_text(song: Dict) -> str:
    """Text used only for TF-IDF indexing/matching.

    Deliberately excludes title/artist: in a 20-song catalog a proper noun
    that happens to share a word with the query (e.g. "Night Drive Loop" for
    a "late-night" query) can outweigh real genre/mood/feel matches. Numeric
    features are turned into descriptive words so a query like "chill and
    acoustic" can match a song's energy/acousticness values, not just its
    genre and mood labels.
    """
    energy_words = _bucket(
        song["energy"], "low energy calm mellow relaxed", "medium energy", "high energy intense energetic",
        0.40, 0.70,
    )
    acoustic_words = _bucket(
        song["acousticness"], "electronic synthetic produced", "semi acoustic", "acoustic unplugged organic",
        0.30, 0.60,
    )
    valence_words = _bucket(
        song["valence"], "sad melancholy somber", "neutral mood", "happy upbeat positive",
        0.40, 0.60,
    )
    dance_words = _bucket(
        song["danceability"], "low danceability contemplative reflective", "moderately danceable", "danceable groovy",
        0.40, 0.70,
    )
    tempo_words = _bucket(
        song["tempo_bpm"], "slow tempo", "medium tempo", "fast tempo uptempo",
        90, 120,
    )
    return (
        f"Genre: {song['genre']}. Mood: {song['mood']}. "
        f"{energy_words}. {acoustic_words}. {valence_words}. {dance_words}. {tempo_words}."
    )


def _song_to_document(song: Dict) -> str:
    """Build the text Claude sees for one song: metadata turned into prose.

    Unlike `_song_to_retrieval_text`, this includes title/artist, since the
    LLM needs to name the song it's recommending.
    """
    return (
        f"{song['title']} by {song['artist']}. "
        f"Genre: {song['genre']}. Mood: {song['mood']}. "
        f"Energy {song['energy']:.2f} out of 1.0. "
        f"Acousticness {song['acousticness']:.2f} out of 1.0. "
        f"Valence {song['valence']:.2f}. Danceability {song['danceability']:.2f}. "
        f"Tempo {song['tempo_bpm']:.0f} bpm."
    )


@dataclass
class _Vector:
    weights: Dict[str, float]
    norm: float


class TfidfIndex:
    """A minimal, dependency-free TF-IDF index with cosine similarity.

    Built from scratch instead of pulling in scikit-learn: the catalog is a
    few dozen songs, so a from-scratch index is simpler to reason about and
    keeps the project's dependency list small.
    """

    def __init__(self, documents: List[str]):
        self._doc_term_counts = [Counter(_tokenize(doc)) for doc in documents]
        self._idf = self._compute_idf(self._doc_term_counts)
        self._doc_vectors = [self._vectorize(counts) for counts in self._doc_term_counts]

    def _compute_idf(self, doc_term_counts: List[Counter]) -> Dict[str, float]:
        n_docs = len(doc_term_counts)
        doc_freq: Counter = Counter()
        for counts in doc_term_counts:
            doc_freq.update(counts.keys())
        # Smoothed IDF so a term appearing in every document still gets a
        # small positive weight instead of zero.
        return {
            term: math.log((1 + n_docs) / (1 + freq)) + 1.0
            for term, freq in doc_freq.items()
        }

    def _vectorize(self, term_counts: Counter) -> _Vector:
        weights = {
            term: count * self._idf.get(term, 0.0) for term, count in term_counts.items()
        }
        norm = math.sqrt(sum(w * w for w in weights.values()))
        return _Vector(weights=weights, norm=norm)

    def _query_vector(self, query: str) -> _Vector:
        counts = Counter(_tokenize(query))
        weights = {
            term: count * self._idf.get(term, 0.0) for term, count in counts.items()
        }
        norm = math.sqrt(sum(w * w for w in weights.values()))
        return _Vector(weights=weights, norm=norm)

    @staticmethod
    def _cosine_similarity(a: _Vector, b: _Vector) -> float:
        if a.norm == 0.0 or b.norm == 0.0:
            return 0.0
        shared_terms = a.weights.keys() & b.weights.keys()
        dot = sum(a.weights[t] * b.weights[t] for t in shared_terms)
        return dot / (a.norm * b.norm)

    def rank(self, query: str) -> List[float]:
        """Return a cosine similarity score for every document, in document order."""
        q_vec = self._query_vector(query)
        return [self._cosine_similarity(q_vec, doc_vec) for doc_vec in self._doc_vectors]


def retrieve(
    query: str, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float]]:
    """Retrieve the top-k songs most relevant to a free-text query.

    Returns (song, similarity_score) pairs sorted by descending score.
    Songs scoring below RELEVANCE_THRESHOLD are dropped: a low-similarity
    "best available" match is often worse than admitting nothing fits.
    """
    if not songs:
        return []

    index = TfidfIndex([_song_to_retrieval_text(song) for song in songs])
    scores = index.rank(query)

    scored = [
        (song, score)
        for song, score in zip(songs, scores)
        if score >= RELEVANCE_THRESHOLD
    ]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:k]


def _build_context(retrieved: List[Tuple[Dict, float]]) -> str:
    lines = []
    for i, (song, score) in enumerate(retrieved, start=1):
        lines.append(f"{i}. {_song_to_document(song)} (relevance {score:.2f})")
    return "\n".join(lines)


# Confidence thresholds for the retrieval-based fallback estimate. These are
# the same boundaries a human skimming the Testing Summary table would land
# on, not a calibrated probability: see `_confidence_from_retrieval` docstring
# and model_card.md's "Confidence scoring" limitation note.
CONFIDENCE_HIGH_CUTOFF = 0.35
CONFIDENCE_MEDIUM_CUTOFF = 0.15

_CONFIDENCE_LINE_RE = re.compile(
    r"confidence:\s*(high|medium|low)\b[^\n]*", re.IGNORECASE
)


def _confidence_from_retrieval(retrieved: List[Tuple[Dict, float]]) -> str:
    """Heuristic confidence derived purely from retrieval similarity scores.

    Used whenever there's no LLM-stated confidence to fall back on (the
    no-match guardrail, the no-API-key path, and any API failure path), so
    that every answer_query() result carries a confidence rating.
    """
    if not retrieved:
        return "None"
    best_score = retrieved[0][1]
    if best_score >= CONFIDENCE_HIGH_CUTOFF:
        return "High"
    if best_score >= CONFIDENCE_MEDIUM_CUTOFF:
        return "Medium"
    return "Low"


def _fallback_answer(retrieved: List[Tuple[Dict, float]], reason: str) -> Tuple[str, str]:
    confidence = _confidence_from_retrieval(retrieved)
    if not retrieved:
        answer = (
            "No songs in the catalog are a good match for that request "
            f"({reason}). Try a different genre, mood, or feeling.\n"
            f"Confidence: {confidence} - no retrieved song cleared the relevance threshold."
        )
        return answer, confidence
    lines = [f"(LLM unavailable: {reason}. Showing retrieved catalog matches directly.)"]
    for song, score in retrieved:
        lines.append(
            f"- {song['title']} by {song['artist']} ({song['genre']}, {song['mood']}, "
            f"relevance {score:.2f})"
        )
    lines.append(
        f"Confidence: {confidence} - based on retrieval relevance only "
        "(no LLM judgment was available for this answer)."
    )
    return "\n".join(lines), confidence


SYSTEM_PROMPT = (
    "You are VibeMatch, a music recommendation assistant for a small song catalog. "
    "You will be given a listener's request and a short numbered list of songs "
    "retrieved from the catalog as the ONLY candidates. "
    "Recommend 1 to 3 songs strictly from that list, referencing each by title and "
    "artist, and explain briefly why each fits the request using the genre, mood, "
    "energy, acousticness, valence, danceability or tempo values given. "
    "Do not recommend, invent, or imply the existence of any song not in the list. "
    "If none of the listed songs genuinely fit the request, say so plainly instead "
    "of forcing a recommendation. "
    "Finish your reply with one final line in exactly this format: "
    "'Confidence: <High|Medium|Low> - <one short reason>', rating how well the "
    "retrieved songs actually satisfy the request (not how fluent your answer is)."
)


def generate_grounded_answer(
    query: str, retrieved: List[Tuple[Dict, float]], model: str = DEFAULT_MODEL
) -> Tuple[str, bool, str]:
    """Ask Claude to answer `query`, grounded only in `retrieved` songs.

    Returns (answer_text, used_llm, confidence). used_llm is False whenever
    the answer came from the deterministic fallback instead of a live model
    call, so callers/tests can tell the two apart. confidence is one of
    "High"/"Medium"/"Low"/"None": the model's own self-rated line when a live
    call succeeds and follows the format, otherwise a heuristic derived from
    retrieval scores (see _confidence_from_retrieval).
    """
    if not retrieved:
        answer, confidence = _fallback_answer(retrieved, "no catalog songs were relevant enough")
        return answer, False, confidence

    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.warning("ANTHROPIC_API_KEY not set; falling back to raw retrieval results.")
        answer, confidence = _fallback_answer(retrieved, "ANTHROPIC_API_KEY is not set")
        return answer, False, confidence

    import anthropic

    context = _build_context(retrieved)
    user_content = f"Listener's request: {query}\n\nCandidate songs:\n{context}"

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=model,
            max_tokens=MAX_ANSWER_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
    except anthropic.AuthenticationError:
        logger.error("Anthropic API key was rejected (authentication error).")
        answer, confidence = _fallback_answer(retrieved, "the Anthropic API key was rejected")
        return answer, False, confidence
    except anthropic.RateLimitError:
        logger.error("Anthropic API rate limit hit.")
        answer, confidence = _fallback_answer(retrieved, "the Anthropic API rate limit was hit")
        return answer, False, confidence
    except anthropic.APIConnectionError:
        logger.error("Could not connect to the Anthropic API.")
        answer, confidence = _fallback_answer(retrieved, "could not connect to the Anthropic API")
        return answer, False, confidence
    except anthropic.APIStatusError as exc:
        logger.error("Anthropic API returned an error: %s", exc)
        answer, confidence = _fallback_answer(retrieved, f"the Anthropic API returned an error ({exc.status_code})")
        return answer, False, confidence

    if response.stop_reason == "refusal":
        logger.warning("Model declined to answer (stop_reason=refusal).")
        answer, confidence = _fallback_answer(retrieved, "the model declined to answer")
        return answer, False, confidence

    text = "".join(block.text for block in response.content if block.type == "text").strip()
    if not text:
        logger.warning("Model returned no text content.")
        answer, confidence = _fallback_answer(retrieved, "the model returned an empty response")
        return answer, False, confidence

    match = _CONFIDENCE_LINE_RE.search(text)
    if match:
        confidence = match.group(1).capitalize()
    else:
        logger.warning("Model response did not include a parseable confidence line; estimating from retrieval instead.")
        confidence = _confidence_from_retrieval(retrieved)

    return text, True, confidence


def answer_query(
    query: str, songs: List[Dict], k: int = 5, model: str = DEFAULT_MODEL
) -> Dict:
    """Full RAG pipeline: retrieve relevant songs, then generate a grounded answer.

    Returns a dict with: query, retrieved ([(song, score), ...]), answer (str),
    used_llm (bool), confidence ("High"/"Medium"/"Low"/"None").
    """
    logger.info("Query received: %r", query)
    retrieved = retrieve(query, songs, k=k)
    logger.info(
        "Retrieved %d/%d songs above threshold %.2f: %s",
        len(retrieved),
        k,
        RELEVANCE_THRESHOLD,
        [song["title"] for song, _ in retrieved],
    )

    answer, used_llm, confidence = generate_grounded_answer(query, retrieved, model=model)
    logger.info(
        "Answer generated via %s with confidence=%s",
        "LLM" if used_llm else "fallback",
        confidence,
    )

    return {
        "query": query,
        "retrieved": retrieved,
        "answer": answer,
        "used_llm": used_llm,
        "confidence": confidence,
    }

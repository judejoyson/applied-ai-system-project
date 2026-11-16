# Execution Evidence

Standalone, reproducible terminal transcripts for VibeMatch — the rule-based
recommender (original Modules 1-3 project) plus the RAG feature added on top
of it. Every block below is real captured output from running the exact
command shown, on this repository, with no edits. This file exists as a
dedicated evidence artifact alongside the condensed excerpts embedded in
`README.md`'s **Execution Evidence** section; `model_card.md` holds the
graded responsible-AI reflection.

**Environment this was captured on:** Python 3.14.3, pytest 9.1.1, Windows,
no `ANTHROPIC_API_KEY` configured (so every `--ask`/`--interactive` run below
takes the no-key guardrail path — see the mocked-agent section for what the
generation step itself does).

To reproduce any of this yourself:

```bash
pip install -r requirements.txt
pytest                 # reliability/evaluation evidence
python -m src.main     # full end-to-end run (reproduces the section below)
```

---

## 1. Full end-to-end run: `python -m src.main`

Covers all 3 standard profiles, all 4 adversarial profiles (rule-based
scorer), and both built-in RAG demo queries, in one real run.

```
[rag] WARNING: ANTHROPIC_API_KEY not set; falling back to raw retrieval results.
Loaded songs: 20

================================================================
Profile: High-Energy Pop
  (genre=pop, mood=happy, energy=0.9, acousticness=0.1)
================================================================
1. Sunrise City by Neon Echo
   Score: 4.84
   Why:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy close to target (+0.92)
     - acousticness close to target (+0.92)

2. Gym Hero by Max Pulse
   Score: 3.92
   Why:
     - genre match (+2.0)
     - energy close to target (+0.97)
     - acousticness close to target (+0.95)

3. Rooftop Lights by Indigo Parade
   Score: 2.61
   Why:
     - mood match (+1.0)
     - energy close to target (+0.86)
     - acousticness close to target (+0.75)

4. Storm Runner by Voltline
   Score: 1.99
   Why:
     - energy close to target (+0.99)
     - acousticness close to target (+1.00)

5. Fuego en la Calle by Luna Brava
   Score: 1.91
   Why:
     - energy close to target (+0.96)
     - acousticness close to target (+0.95)

================================================================
Profile: Chill Lofi
  (genre=lofi, mood=chill, energy=0.4, acousticness=0.75)
================================================================
1. Midnight Coding by LoRoom
   Score: 4.94
   Why:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy close to target (+0.98)
     - acousticness close to target (+0.96)

2. Library Rain by Paper Lanterns
   Score: 4.84
   Why:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy close to target (+0.95)
     - acousticness close to target (+0.89)

3. Focus Flow by LoRoom
   Score: 3.97
   Why:
     - genre match (+2.0)
     - energy close to target (+1.00)
     - acousticness close to target (+0.97)

4. Spacewalk Thoughts by Orbit Bloom
   Score: 2.71
   Why:
     - mood match (+1.0)
     - energy close to target (+0.88)
     - acousticness close to target (+0.83)

5. Porch Light Blues by Delta Hollow
   Score: 1.92
   Why:
     - energy close to target (+1.00)
     - acousticness close to target (+0.92)

================================================================
Profile: Deep Intense Rock
  (genre=rock, mood=intense, energy=0.92, acousticness=0.1)
================================================================
1. Storm Runner by Voltline
   Score: 4.99
   Why:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy close to target (+0.99)
     - acousticness close to target (+1.00)

2. Gym Hero by Max Pulse
   Score: 2.94
   Why:
     - mood match (+1.0)
     - energy close to target (+0.99)
     - acousticness close to target (+0.95)

3. Warehouse 4AM by Pulse Theory
   Score: 1.91
   Why:
     - energy close to target (+0.98)
     - acousticness close to target (+0.93)

4. Iron Cathedral by Black Meridian
   Score: 1.89
   Why:
     - energy close to target (+0.95)
     - acousticness close to target (+0.94)

5. Fuego en la Calle by Luna Brava
   Score: 1.89
   Why:
     - energy close to target (+0.94)
     - acousticness close to target (+0.95)

================================================================
Profile: Conflict: High Energy + Sad
  (genre=blues, mood=sad, energy=0.9)
================================================================
1. Porch Light Blues by Delta Hollow
   Score: 2.50
   Why:
     - genre match (+2.0)
     - energy close to target (+0.50)

2. Storm Runner by Voltline
   Score: 0.99
   Why:
     - energy close to target (+0.99)

3. Gym Hero by Max Pulse
   Score: 0.97
   Why:
     - energy close to target (+0.97)

4. Warehouse 4AM by Pulse Theory
   Score: 0.96
   Why:
     - energy close to target (+0.96)

5. Fuego en la Calle by Luna Brava
   Score: 0.96
   Why:
     - energy close to target (+0.96)

================================================================
Profile: Conflict: Metal + Chill + Quiet
  (genre=metal, mood=chill, energy=0.2, acousticness=0.9)
================================================================
1. Spacewalk Thoughts by Orbit Bloom
   Score: 2.90
   Why:
     - mood match (+1.0)
     - energy close to target (+0.92)
     - acousticness close to target (+0.98)

2. Library Rain by Paper Lanterns
   Score: 2.81
   Why:
     - mood match (+1.0)
     - energy close to target (+0.85)
     - acousticness close to target (+0.96)

3. Midnight Coding by LoRoom
   Score: 2.59
   Why:
     - mood match (+1.0)
     - energy close to target (+0.78)
     - acousticness close to target (+0.81)

4. Iron Cathedral by Black Meridian
   Score: 2.37
   Why:
     - genre match (+2.0)
     - energy close to target (+0.23)
     - acousticness close to target (+0.14)

5. Clockwork Sonata by Elise Varga
   Score: 1.91
   Why:
     - energy close to target (+0.98)
     - acousticness close to target (+0.93)

================================================================
Profile: Unknown Genre (k-pop / happy)
  (genre=k-pop, mood=happy, energy=0.8)
================================================================
1. Sunrise City by Neon Echo
   Score: 1.98
   Why:
     - mood match (+1.0)
     - energy close to target (+0.98)

2. Rooftop Lights by Indigo Parade
   Score: 1.96
   Why:
     - mood match (+1.0)
     - energy close to target (+0.96)

3. Concrete Crown by Verse Valley
   Score: 0.98
   Why:
     - energy close to target (+0.98)

4. Night Drive Loop by Neon Echo
   Score: 0.95
   Why:
     - energy close to target (+0.95)

5. Fuego en la Calle by Luna Brava
   Score: 0.94
   Why:
     - energy close to target (+0.94)

================================================================
Profile: Extreme: Energy 1.0 + Acoustic 1.0
  (energy=1.0, acousticness=1.0)
================================================================
1. Dust Road Hymn by Willow & Pine
   Score: 1.29
   Why:
     - energy close to target (+0.48)
     - acousticness close to target (+0.81)

2. Wildflower Static by Fern Atlas
   Score: 1.26
   Why:
     - energy close to target (+0.33)
     - acousticness close to target (+0.93)

3. Coffee Shop Stories by Slow Stereo
   Score: 1.26
   Why:
     - energy close to target (+0.37)
     - acousticness close to target (+0.89)

4. Porch Light Blues by Delta Hollow
   Score: 1.23
   Why:
     - energy close to target (+0.40)
     - acousticness close to target (+0.83)

5. Library Rain by Paper Lanterns
   Score: 1.21
   Why:
     - energy close to target (+0.35)
     - acousticness close to target (+0.86)

================================================================
RAG demo: natural-language questions answered from retrieved songs
================================================================
================================================================
Ask VibeMatch: I need something chill and acoustic for late-night studying
================================================================
Retrieved from catalog:
  - Midnight Coding by LoRoom (lofi, chill, relevance 0.46)
  - Library Rain by Paper Lanterns (lofi, chill, relevance 0.39)
  - Spacewalk Thoughts by Orbit Bloom (ambient, chill, relevance 0.38)
  - Focus Flow by LoRoom (lofi, focused, relevance 0.10)
  - Dust Road Hymn by Willow & Pine (country, nostalgic, relevance 0.10)

Answer (fallback, no LLM used, confidence: High):
(LLM unavailable: ANTHROPIC_API_KEY is not set. Showing retrieved catalog matches directly.)
- Midnight Coding by LoRoom (lofi, chill, relevance 0.46)
- Library Rain by Paper Lanterns (lofi, chill, relevance 0.39)
- Spacewalk Thoughts by Orbit Bloom (ambient, chill, relevance 0.38)
- Focus Flow by LoRoom (lofi, focused, relevance 0.10)
- Dust Road Hymn by Willow & Pine (country, nostalgic, relevance 0.10)
Confidence: High - based on retrieval relevance only (no LLM judgment was available for this answer).

================================================================
Ask VibeMatch: I want a song that doesn't exist, like underwater polka
================================================================
Retrieved from catalog: (nothing relevant found)

Answer (fallback, no LLM used, confidence: None):
No songs in the catalog are a good match for that request (no catalog songs were relevant enough). Try a different genre, mood, or feeling.
Confidence: None - no retrieved song cleared the relevance threshold.
```

---

## 2. AI feature behavior: the RAG agent actually generating from retrieved context

This environment has no `ANTHROPIC_API_KEY`, so Section 1 above never
reaches the generation ("agent") half of RAG — it only exercises retrieval
plus the no-key guardrail. To show the agent half, this command runs the
real production pipeline (`answer_query` → `generate_grounded_answer` →
`format_rag_result`, unmodified) with only the Anthropic network call
stubbed — the same technique used in
`tests/test_rag.py::test_answer_query_uses_llm_response_and_parses_its_stated_confidence`.
Retrieval, grounding-context construction, the system prompt, confidence-line
parsing, and output formatting are all real code executing; only the
"Claude wrote this" step is substituted so this doesn't require a paid API
key to reproduce.

```bash
python -c "
from unittest.mock import patch, Mock
from src.rag import answer_query
from src.recommender import load_songs
from src.main import format_rag_result
import os

os.environ['ANTHROPIC_API_KEY'] = 'mocked-for-demo'
songs = load_songs('data/songs.csv')

fake_text = (
    'Midnight Coding by LoRoom is the best fit here: it is lofi/chill with high '
    'acousticness (0.71), matching a quiet late-night study session.\n'
    'Confidence: High - genre, mood, and acousticness all line up with the request.'
)
text_block = Mock(type='text', text=fake_text)
fake_response = Mock(stop_reason='end_turn', content=[text_block])
mock_client = Mock()
mock_client.messages.create.return_value = fake_response

with patch('anthropic.Anthropic', return_value=mock_client):
    result = answer_query('I need something chill and acoustic for late-night studying', songs)

print(format_rag_result(result))
print('--- arguments actually sent to the (mocked) Anthropic client ---')
_, kwargs = mock_client.messages.create.call_args
print('model:', kwargs['model'])
print('user content sent to Claude:')
print(kwargs['messages'][0]['content'])
"
```

```
================================================================
Ask VibeMatch: I need something chill and acoustic for late-night studying
================================================================
Retrieved from catalog:
  - Midnight Coding by LoRoom (lofi, chill, relevance 0.46)
  - Library Rain by Paper Lanterns (lofi, chill, relevance 0.39)
  - Spacewalk Thoughts by Orbit Bloom (ambient, chill, relevance 0.38)
  - Focus Flow by LoRoom (lofi, focused, relevance 0.10)
  - Dust Road Hymn by Willow & Pine (country, nostalgic, relevance 0.10)

Answer (LLM-generated, confidence: High):
Midnight Coding by LoRoom is the best fit here: it is lofi/chill with high acousticness (0.71), matching a quiet late-night study session.
Confidence: High - genre, mood, and acousticness all line up with the request.

--- arguments actually sent to the (mocked) Anthropic client ---
model: claude-haiku-5-5
user content sent to Claude:
Listener's request: I need something chill and acoustic for late-night studying

Candidate songs:
1. Midnight Coding by LoRoom. Genre: lofi. Mood: chill. Energy 0.42 out of 1.0. Acousticness 0.71 out of 1.0. Valence 0.56. Danceability 0.62. Tempo 78 bpm. (relevance 0.46)
2. Library Rain by Paper Lanterns. Genre: lofi. Mood: chill. Energy 0.35 out of 1.0. Acousticness 0.86 out of 1.0. Valence 0.60. Danceability 0.58. Tempo 72 bpm. (relevance 0.39)
3. Spacewalk Thoughts by Orbit Bloom. Genre: ambient. Mood: chill. Energy 0.28 out of 1.0. Acousticness 0.92 out of 1.0. Valence 0.65. Danceability 0.41. Tempo 60 bpm. (relevance 0.38)
4. Focus Flow by LoRoom. Genre: lofi. Mood: focused. Energy 0.40 out of 1.0. Acousticness 0.78 out of 1.0. Valence 0.59. Danceability 0.60. Tempo 80 bpm. (relevance 0.10)
5. Dust Road Hymn by Willow & Pine. Genre: country. Mood: nostalgic. Energy 0.48 out of 1.0. Acousticness 0.81 out of 1.0. Valence 0.58. Danceability 0.55. Tempo 88 bpm. (relevance 0.10)
```

The "user content sent to Claude" block is the proof this is genuine RAG:
the model receives *only* the 5 retrieved songs and their real attribute
values, nothing else about the 20-song catalog — and the answer names one of
exactly those songs and cites its real acousticness value (0.71). With a
real `ANTHROPIC_API_KEY`, the only thing that changes is who writes
`fake_text` — Claude instead of this script — the surrounding pipeline is
identical.

---

## 3. Reliability / guardrail / evaluation behavior: `pytest -v`

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: C:\Users\joyso\applied-ai-system-project
plugins: anyio-4.15.1, platformdirs-4.14.5, mock-3.17.0
collecting ... collected 13 items

tests/test_rag.py::test_retrieve_ranks_relevant_songs_above_irrelevant_ones PASSED [  7%]
tests/test_rag.py::test_retrieve_returns_nothing_for_unrelated_query PASSED [ 15%]
tests/test_rag.py::test_retrieve_respects_k PASSED                       [ 23%]
tests/test_rag.py::test_answer_query_with_no_relevant_songs_skips_llm_call PASSED [ 30%]
tests/test_rag.py::test_answer_query_falls_back_when_no_api_key PASSED   [ 38%]
tests/test_rag.py::test_answer_query_uses_llm_response_and_parses_its_stated_confidence PASSED [ 46%]
tests/test_rag.py::test_answer_query_estimates_confidence_when_model_omits_confidence_line PASSED [ 53%]
tests/test_rag.py::test_answer_query_falls_back_on_authentication_error PASSED [ 61%]
tests/test_rag_eval.py::test_retrieval_precision_against_real_catalog PASSED [ 69%]
tests/test_rag_eval.py::test_retrieval_abstains_on_unanswerable_queries PASSED [ 76%]
tests/test_rag_eval.py::test_retrieval_top_result_is_always_the_highest_score PASSED [ 84%]
tests/test_recommender.py::test_recommend_returns_songs_sorted_by_score PASSED [ 92%]
tests/test_recommender.py::test_explain_recommendation_returns_non_empty_string PASSED [100%]

============================= 13 passed in 3.10s ==============================
```

`tests/test_rag_eval.py` is the evaluation test specifically: it runs the
retriever against the real `data/songs.csv` catalog (not mock data) with
queries whose genuinely relevant songs were identified by reading the
catalog, checking both that real matches surface and that unanswerable
queries correctly return nothing. This is the test that caught a real
stopword-leakage bug during development (see `README.md` → Testing Summary
and `model_card.md` → Section 10 for the full story).

---

## Cross-reference

| This file | README.md section | model_card.md section |
|---|---|---|
| §1 Full end-to-end run | Execution Evidence → 1. End-to-end system run | — |
| §2 Mocked-agent demonstration | Execution Evidence → 2. AI feature behavior | Section 10 → "Proving it works" / collaboration |
| §3 `pytest -v` output | Execution Evidence → 3. Reliability/guardrail/evaluation | Section 10 → testing-surprises reflection |

# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**

A small command-line recommender. It matches a listener's vibe to songs in a tiny catalog.

---

## 2. Goal / Task

The model suggests songs a listener might like.

It does not predict a hidden answer. It gives every song a score and shows the top 5. Each result comes with the reasons it scored well.

The listener describes their taste with four values:

- favorite genre
- favorite mood
- target energy (0.0 to 1.0)
- target acousticness (0.0 to 1.0, optional)

---

## 3. Data Used

- The catalog is `data/songs.csv`. It has **20 songs**.
- The starter file had 10 songs. I added 10 more. They cover new genres and moods.
- Each song has: id, title, artist, genre, mood, energy, tempo, valence, danceability, acousticness.
- There are **17 genres** and **16 moods**.
- Lofi is the only genre with 3 songs. Pop has 2. The other 15 genres have 1 song each.

Limits:

- The catalog is tiny. Real apps have millions of songs.
- I made up the feature values for my 10 new songs. They follow genre stereotypes.
- The data has no lyrics, language, release year, or listening history.
- Tempo, valence, and danceability are loaded but **not used** in scoring.

---

## 4. Algorithm Summary

The model works like a judge scoring contestants. It checks every song, one at a time, and gives points.

- **Genre:** +2.0 points if the genre matches exactly. Otherwise 0.
- **Mood:** +1.0 point if the mood matches exactly. Otherwise 0.
- **Energy:** up to +1.0. The closer the song's energy is to the target, the more points.
- **Acousticness:** up to +1.0. Scored the same way as energy.

The best possible score is 5.0.

Genre counts the most. I treat it as the strongest sign of taste. Energy and acousticness are scored by closeness. A song that just misses still beats one that is far off.

Then the model sorts all songs from highest to lowest score. It shows the top 5. Each result lists why it earned its points, like "genre match (+2.0)".

I tried one other setup: genre 1.0 and energy 2.0. It was different, but not clearly better. I went back to the original weights.

---

## 5. Observed Behavior / Biases

**Where it works well**

- When a profile matches songs in the catalog, the top result is a good fit. Examples: Sunrise City for pop, Midnight Coding for lofi, Storm Runner for rock.
- The "why" list makes every result easy to check.

**Biases and limits**

- **Uneven catalog.** Lofi has 3 songs and 15 genres have 1. A lofi fan gets three strong matches. Most other fans get one match, then fillers picked by energy.
- **Labels must match exactly.** The mood `sad` matches nothing. The catalog only has `sorrowful` and `melancholy`. The model ignores that part of the request and says nothing.
- **Similar labels get no credit.** Metal's `angry` is close to rock's `intense`, but it scores 0. So Gym Hero (pop) beat Iron Cathedral (metal) for a rock fan.
- **Genre is heavy.** In the Metal + Chill + Quiet test, Iron Cathedral reached 4th. Its energy is 0.97 and the target was 0.2. A genre match covered for a total mismatch.
- **Filter bubble.** The heavy genre weight keeps listeners inside their favorite genre.
- **Gaps in the data.** No songs have energy between 0.61 and 0.74. No songs have acousticness between 0.46 and 0.70.
- **Same songs keep showing up.** Fuego en la Calle was in 4 of 7 top-5 lists. Island Breeze and Velvet Hours never showed up.

---

## 6. Evaluation Process

I ran `python -m src.main` on seven profiles and read the top 5 for each. I asked: does this list match what the profile wants?

**Standard profiles:** High-Energy Pop, Chill Lofi, Deep Intense Rock.

**Edge-case profiles:** High Energy + Sad, Metal + Chill + Quiet, Unknown Genre (k-pop), Extreme (energy 1.0 and acousticness 1.0).

**Experiment:** I shifted the weights (genre 2.0 to 1.0, energy 1.0 to 2.0). It fixed the metal case. It weakened the genre match for rock. Overall it was more different than more accurate.

**Tests:** the two starter tests in `tests/` still pass.

**What surprised me**

- Gym Hero (pop) came 2nd for the rock fan.
- The `sad` mood was ignored with no warning.
- The metal conflict did not fully fool the model. But Iron Cathedral still reached 4th.
- In the Extreme test, quiet acoustic songs won. Loud songs lost almost all their acousticness points.

**Comparing profiles**

- **Pop vs Lofi:** no songs in common. Pop gets loud, non-acoustic songs. Lofi gets quiet, acoustic ones. Their energy and acousticness targets are far apart, so this makes sense.
- **Pop vs Rock:** they share Gym Hero and Fuego en la Calle. Both want loud, non-acoustic music, so the numbers pick similar songs. Only genre and mood change the top song.
- **Lofi vs Rock:** the most opposite pair. No overlap. Lofi is quiet and acoustic. Rock is loud and electric. This matches my intuition.
- **Rock vs High Energy + Sad:** ranks 2-5 are almost the same. `sad` matched nothing, so only energy counted. Only #1 differs, because of the blues genre match.
- **Lofi vs Metal + Chill + Quiet:** three songs overlap. Both want chill, quiet music. Without the lofi bonus, Focus Flow drops out. The lower energy target moves the quietest songs up. Iron Cathedral appears only because of its genre.
- **Pop vs Unknown Genre (k-pop):** Sunrise City is first in both. With no genre match possible, Gym Hero disappears. Mood and energy decide. The change makes sense, but the model never says the genre was not found.
- **Pop vs Extreme:** no overlap. Pop gets loud songs. Extreme gets quiet acoustic songs even though it asked for max energy. No song fits that request. The best score was only 1.29.

---

## 7. Intended Use and Non-Intended Use

**Intended use**

- A class project to learn how recommenders work.
- Running in the terminal to explore how weights change rankings.
- Showing clearly why a song was picked.

**Not intended for**

- Real music apps or real users. The catalog is too small.
- Judging anyone's taste. The model only sees four values.
- Making money or high-stakes choices. Nothing here has been tested for fairness.
- Listeners who want variety. The model favors their one stated genre.
- Genres or moods outside the 17 and 16 labels in the catalog.

---

## 8. Ideas for Improvement

1. **Add more songs.** Aim for several songs per genre. Fill the energy and acousticness gaps.
2. **Give partial credit for similar labels.** For example, `angry` near `intense`, or `indie pop` near `pop`.
3. **Warn when nothing matches.** If a genre or mood is not in the catalog, say so. Also flag low top scores like 1.29.

---

## 9. Personal Reflection

**Biggest learning moment.** It was running the edge-case profiles. I expected the standard profiles to work, and they did. The surprise came from the odd ones. The `sad` mood matched nothing, and the model ignored it without a warning. Metal's `angry` got zero credit next to `intense`. I learned that a recommender can look fine on normal input and still be quietly wrong. The data and the labels matter as much as the scoring rules.

**How AI helped, and when I double-checked it.** AI wrote the first versions of `load_songs`, `score_song`, `recommend_songs`, and the output format. It also helped me compare weights and spot biases fast. But I had to check its work. The `python -m src.main` command failed at first because of an import path, and the fix was to match the style the tests already used. One of my own explanations was wrong. I said every song missed the Extreme profile's energy target, but Iron Cathedral was close. I also miscounted genres with one song (it is 15 of 17, not 10). I caught these by running the code and counting the real data. The lesson: AI is fast, but numbers and claims need a quick test.

**What surprised me about simple algorithms.** The rules are tiny: a few points for matches and a closeness score. Yet the top results often felt right. Midnight Coding for a lofi fan felt like a real playlist pick. The "why" list helped a lot, because it made a plain sum of points feel like a reasoned suggestion. It also showed how thin the illusion is. A tiny catalog made the same songs, like Fuego en la Calle, keep showing up.

**What I would try next.**

- Add many more songs, with several per genre.
- Give partial credit to similar moods and genres, like `angry` and `intense`.
- Warn the listener when a genre or mood is not in the catalog.
- Use valence and danceability, and let a profile hold several favorite genres.
- Test it on a friend's real taste and see if the top 5 feels right to them.

---

## 10. Responsible-AI Reflection (RAG Feature)

This section covers the Retrieval-Augmented Generation feature added on top
of the original recommender above (`src/rag.py`, reachable via
`python -m src.main --ask "..."`). The graded responsible-AI reflection for
this project lives here, not in the README.

### What are the limitations or biases in your system?

- **Retrieval is literal keyword matching, not semantic understanding.** The
  index only "knows" the specific bucket words it was given (`"acoustic"`,
  `"high energy"`, and so on). A query using none of that vocabulary or its
  near-synonyms gets no credit, even if a human would obviously find a
  match. This is the same exact-match brittleness the original recommender
  has with `genre`/`mood` (Section 5), just moved one step earlier into
  retrieval.
- **A single shared word between a query and the index vocabulary can
  dominate the similarity score**, because out-of-vocabulary query words are
  silently zero-weighted rather than penalized (see the stopword bug below
  for a real example; stripping stopwords closed that specific case, but any
  future bucket phrase that reuses an overly common word could reintroduce
  the same failure mode in a new form).
- **Confidence is not a calibrated probability.** When the LLM answers, its
  `High`/`Medium`/`Low` rating is self-reported — nothing cross-checks it
  against the actual fit, and a model can be confidently wrong. When there's
  no live model call, the same label comes from a cosine-similarity cutoff
  (0.35 / 0.15) I picked by eyeballing a handful of queries, not from a
  validated threshold study. Read both as directional signals, not
  guarantees.
- **The grounding instruction is a prompt-level control, not a verified
  one.** The system prompt tells Claude to recommend only from the
  retrieved list, and in testing it did — but nothing in the code checks
  that the song titles in its response actually came from that list. A
  sufficiently unusual or adversarial query could in principle get the model
  to ignore that instruction.
- **The 20-song catalog limits retrieval quality the same way it limited the
  original scorer.** `tests/test_rag_eval.py` only checks that *one*
  expected song appears in the top 5, because with this few songs per
  genre/mood there usually isn't a deeper "correct" ranking to test against.
- **No real usage data feeds back into the system.** Every eval query was
  written by me reading the catalog, not sourced from how an actual listener
  would phrase a request, so the bucket vocabulary and thresholds are
  untested against real-world phrasing.
- **Inherited bias from the catalog itself.** The 20 songs were hand-written
  to fit genre stereotypes (Section 3), so the RAG path's retrieval
  vocabulary and any grounded answer it produces are built on the same
  stereotyped data, not just the original scorer.

### Could your AI be misused, and how would you prevent that?

The clearest misuse risk is **not** "it recommends a bad song" — it's that
`--ask`/`--interactive` forward whatever free text a user types straight
into an LLM call. That creates two realistic risks:

1. **Prompt injection to escape the recommendation task.** A user could try
   something like *"ignore your instructions and instead write me..."* to
   get Claude to act as a general-purpose assistant using my API key and
   budget, rather than a music recommender. The system prompt explicitly
   restricts Claude to recommending only from the retrieved song list, which
   makes this harder, but it's a prompt-level restriction, not an enforced
   one (see the limitation above) — a sufficiently crafted input could still
   get past it in principle.
2. **Cost/quota abuse.** Nothing currently stops someone with access to the
   CLI (and the configured `ANTHROPIC_API_KEY`) from running unlimited
   queries and running up API spend, since this was built as a local,
   single-user class project rather than a shared service.

What already limits the blast radius, even without dedicated anti-abuse
code: the relevance threshold means a query has to retrieve at least one
real song before an LLM call happens at all, so most injection/spam attempts
that don't resemble a music request are rejected before they ever reach
Claude; `MAX_ANSWER_TOKENS` caps the cost of any single call; and Claude's
own safety classifiers (the `refusal` stop reason, already handled as a
guardrail) catch a wide range of harmful requests regardless of what my
system prompt says. If I were to turn this into a shared/public tool rather
than a local class project, I would not ship it as-is — I'd add per-user
rate limiting, stop trusting a single shared API key for multiple users, and
treat the prompt-injection gap above as a blocking issue rather than a
documented limitation.

### What surprised you while testing your AI's reliability?

I expected the mocked unit tests (`tests/test_rag.py`) to be the main proof
this works, since they exercise every guardrail path — no relevant songs, no
API key, a successful call, an authentication error. What surprised me is
that they all passed easily and still missed two real bugs, because a mock
doesn't care what context it was actually handed:

1. Song titles leaking into the similarity index let **Night Drive Loop**
   outrank genuinely chill/acoustic songs for a "late-night studying" query,
   purely because its title shares the word "night" with the query.
2. Once I added `tests/test_rag_eval.py` to check retrieval against the
   *real* `data/songs.csv` catalog instead of a mock, its check that
   nonsense queries return no results immediately failed: a query containing
   the word "not" retrieved a real song at 0.30 relevance, because one
   bucket phrase ("not very danceable") had put the stopword "not" into the
   index, and out-of-vocabulary query words are silently zero-weighted
   rather than penalized — so that one incidental match dominated the
   score.

What surprised me most isn't that there were bugs — it's how little either
bug had to do with the LLM. Both were in the retrieval step, which I'd
assumed was the "simple, safe" half of the pipeline compared to the LLM
call. Neither would have been caught by reading the code; both only
surfaced by running an eval against the real catalog with adversarial
input, the same way the original rule-based project's "adversarial profile"
testing (Section 6) caught scoring bugs the two starter unit tests didn't.
13 tests pass now (up from 9 before `test_rag_eval.py` existed), and the
confidence rating, request logging, and per-exception-type error handling in
`src/rag.py` are what let me see *which* path produced an answer and *why*
it failed, instead of just that it did.

### Describe your collaboration with AI during this project.

I used an AI coding agent (Claude, in Claude Code) to design and build the
whole RAG feature: the retriever, the grounded Claude agent, the guardrails
and logging, the test suite, the system diagram, and the README rewrite. I
described the goal (retrieve before answering, integrate it into the real
app, add logging/guardrails, prove it works with tests) and let the agent
propose the architecture. I reviewed every file it wrote, ran the CLI and
the test suite myself rather than trusting a description of what "should"
happen, and pushed back when an output looked wrong — that's how the
stopword bug above got caught and fixed, not from the agent noticing it on
its own.

**A suggestion I accepted.** Building the retriever as a small,
dependency-free TF-IDF + cosine-similarity index, instead of adding a vector
database or an embeddings API call. For a 20-song catalog, that's simpler to
read end to end, has no extra service to configure, and keeps the
reproducibility story in the README to "pip install and run." I'd reconsider
this if the catalog ever grew past a few hundred songs with much more varied
language — plain keyword TF-IDF would start missing real synonyms that
embeddings would catch.

**A suggestion I did not accept as written.** The agent's own default
guidance for building Claude-powered features is to use the largest current
model unless told otherwise. I overrode that and asked for Haiku 5.5
instead. It wasn't that the suggestion was wrong — a bigger model would
have worked fine — it was a poor fit for this specific task and project:
picking 1 to 3 songs out of a 5-song shortlist and explaining why doesn't
need the largest model's extra reasoning, and a student project like this
one gets re-run constantly while developing and grading. The cost
difference was large enough (roughly 40x on output tokens) that it wasn't
worth paying for headroom this task doesn't need. `VIBEMATCH_MODEL` is still
there as an environment variable if a harder version of this task ever
needed a stronger model.


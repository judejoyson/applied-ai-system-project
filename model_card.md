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

# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

The recommender works like a judge scoring contestants. The listener tells it their
favorite genre, favorite mood, how energetic they want the music to be, and
(optionally) how acoustic they want it. The system then looks at every song in the
catalog, one at a time, and awards points for how well the song fits:

- **Genre:** 2 points if the song's genre is exactly the listener's favorite, 0 if not.
- **Mood:** 1 point if the song's mood is exactly the listener's favorite, 0 if not.
- **Energy:** up to 1 point, depending on how close the song's energy is to the
  listener's target. A perfect match earns the full point, and the further away the
  song is, the fewer points it gets.
- **Acoustic feel:** up to 1 point, awarded the same way as energy.

Genre counts the most because it is the strongest signal of taste. Energy and acoustic
feel are scored by closeness rather than all-or-nothing, so a song that just misses
still beats one that is far off.

Once every song has a total, the system sorts them from highest to lowest and shows
the top few. Each result also lists the reasons it earned its points, such as "genre
match (+2.0)", so the listener can see why a song was picked rather than just trusting
a number.

Changes from the starter: the starter only returned the first songs in the file with a
placeholder explanation. This version loads the catalog from a CSV, scores each song
with the rules above, ranks them, and explains each result. It is a command-line
program (run with `python -m src.main`), with no web or app interface.

Things the scoring ignores: tempo, valence (how positive a song feels) and
danceability are in the data but are not used yet.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

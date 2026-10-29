# English Review

Offline review app (installable PWA) for the easypeasy English classes: vocabulary, grammar,
functional language and common mistakes, with spaced repetition.

- 487 questions · 36 theory sections · 28 presentations covered (as of 2026-10-28)
- Progress lives only in the phone's browser. Back it up from **Ajustes › Exportar progreso**.

## Publish on GitHub Pages (first time)

1. Create a **public** repository called `english-review`.
2. Upload the **contents** of this folder to the root of the repo (not inside a subfolder).
3. Settings › Pages › Branch `main`, folder `/ (root)` › Save.
4. After ~2 minutes it is live at `https://<your-user>.github.io/english-review/`.
   If you use another repo name, change `rutaBase` in `config.json` to `/<repo-name>/`.
5. Open it on your phone and choose **Add to Home Screen**. It then works offline.

## Use it locally (without GitHub)

```bash
cd english-review
python3 -m http.server 8000
# open http://localhost:8000
```

## Add new lessons

All content is generated from `fuente/`. Never edit `contenido.json`, `teoria.json` or `parciales/` by hand.

```
fuente/
  lecciones/NN-slug.json   vocabulary of each speaking lesson (questions are generated automatically)
  preguntas/*.json         hand-written questions (grammar, functional language, mistakes)
  teoria_base.json         theory sections for grammar and functional language
tools/
  generar.py               builds the app from fuente/ and validates it
  extraer_easypeasy.js     console snippet that downloads the text of all presentations
```

1. **New speaking lesson** → add `fuente/lecciones/20-new-slug.json`:

   ```json
   {"n": 20, "slug": "new-slug", "lesson": "Lesson title", "type": "Speaking",
    "skill": "Skill practised",
    "words": [
      {"w": "to tackle", "pos": "verb", "es": "abordar", "def": "to deal with a difficult task directly",
       "ex": "I always {tackle} the bathroom first.", "syn": "to take on", "opp": "to avoid"}
    ]}
   ```
   Wrap the target word inside the example in `{ }`. `syn` / `opp` are optional.

2. **New grammar lesson** → add a section to `fuente/teoria_base.json` and a file
   `fuente/preguntas/g10-topic.json` (copy the format of the existing ones; `correcta` is the index
   of the right option; ids like `g-topic-001`).

3. Build and bump the version so phones download the update:

   ```bash
   python3 tools/generar.py 2026-11-15 --publicar
   ```

4. Upload the changed files to GitHub. On the phone a banner appears: *Hay una versión nueva · Actualizar*.

**Rules that protect your progress:** never change `app.id` in `config.json`, and never rename a
lesson `slug` or a word `w` once published (question ids are built from them). Adding is always safe.

The quickest way: run `tools/extraer_easypeasy.js` on the Resources page, then give the downloaded
text file to Claude and ask it to add the new lessons.

# searchaltright

fan-made transcript search for the altruistic righteousness podcast. not affiliated with the show.

live at https://searchaltright.net

pushing to main rebuilds the site automatically.

## files

- `srt/` - episode transcripts, named like `Episode 49 - Title.srt`
- `episodes.json` - youtube links
- `dates.json` - release dates (US eastern, `"50": "2026-11-17"`)
- `titles.txt` - titles with characters windows won't allow in filenames
- `corrections.txt` - fixes for misheard words
- `static/` - icons and link preview image
- `template.html` - the page
- `build.py` - builds `index.html` and `data.js`

## new episode

1. transcribe it
2. upload the srt to `srt/`
3. add the youtube link to `episodes.json` and the date to `dates.json`

## corrections

one per line in `corrections.txt`:

```
wrong => right
DELETE: line to remove
```

whole words, not case sensitive. the srt files themselves aren't changed.

the build also trims lines whisper repeats over and over.

## run locally

`python build.py`, then open `index.html`.

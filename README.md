# Altruistic Righteousness transcript search

A fan-made search engine for the Altruistic Righteousness podcast. Not affiliated with the show.

**Live at https://searchaltright.net**

Everything in this folder builds one page. Whenever a file here changes on GitHub, the site rebuilds and goes live by itself within a couple of minutes (see the **Actions** tab to watch it happen).

## What's in here

| File / folder | What it is | Do you edit it? |
| --- | --- | --- |
| `srt/` | One transcript per episode | Yes, add new ones here |
| `corrections.txt` | Misheard words to fix, e.g. `Akash => Aakash` | Yes |
| `episodes.json` | YouTube link for each episode | Yes |
| `template.html` | The page design and search code | Only to change the site itself |
| `build.py` | Combines everything into the site | No |
| `.github/workflows/deploy.yml` | Tells GitHub to rebuild on every change | No |

## Adding a new episode (weekly)

1. Transcribe it with `Transcribe.bat` on the PC.
2. Make sure the file is named like `Episode 49 - Episode Title.srt`. The site reads the number and title from the name.
3. On GitHub, open the `srt` folder, click **Add file > Upload files**, drag the .srt in, and click **Commit changes**.
4. Optional: add the YouTube link to `episodes.json` (see below).

The site updates itself a minute or two later.

## Fixing misheard words

Open `corrections.txt` on GitHub, click the pencil icon, and add a line:

```
wrong spelling => Right Spelling
DELETE: a line Whisper made up
```

Capitals don't matter and it only matches whole words. The .srt files are never changed, so deleting a line undoes it. Use the site's search to find mistakes: search the wrong and right spellings and compare the counts.

## Adding YouTube links

Open `episodes.json`, click the pencil icon, and paste each episode's link between the quotes:

```
"48": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
```

Full links or just the video ID both work. Keep the commas between lines and no comma after the last one. Once a link is in, every timestamp for that episode gets a "watch" link that opens YouTube at that moment.

## Testing on your own computer (optional)

With Python installed, run `python build.py` in this folder, then open the `index.html` it creates.

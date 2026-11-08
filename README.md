# GitRex 🦖

**Your GitHub activity grows a T-Rex.** An independently implemented Python renderer that transforms GitHub contribution-calendar data into an animated GIF for a profile README. This release ships new **AI-generated, original-to-this-project dinosaur and forest illustrations**, plus a separately authored **fully procedural** asset set. No images from the earlier user-uploaded T-Rex photo are bundled.

> **Version 2.0.0** · Python 3.10+ · MIT · Offline preview · GitHub Actions · No paid server required

![GitRex demonstration animation](output/trex.gif)

**Note:** The above is a **synthetic demonstration** and is intentionally stamped `DEMO DATA`. Run live collection to show your own contributions.

## Try it without installing anything

1. Download and **extract** the ZIP to a folder.
2. Double-click `OPEN_PREVIEW.html`. Move the contributions slider to grow the dinosaur.
3. Open `output/preview.html` to see the pre-rendered GIF.

The browser preview is self-contained HTML/JS and uses local images. You do not need Node, a backend server, credentials, or an internet connection.

## Regenerate the demo animation (Windows)

Install Python 3.10+ and double-click `RUN_DEMO.bat`. It builds a local `.venv`, installs Pillow and regenerates `output/trex.gif`, `output/trex.png`, `output/preview.html`, and `output/summary.json`.

Or in PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
.venv\Scripts\python.exe -m gitrex demo --output-dir output
```

## Use live GitHub data

1. Install [GitHub CLI](https://cli.github.com/) and Python 3.10+.
2. Run `gh auth login` in PowerShell. Do **not** write tokens into `.env` files or commit them.
3. Double-click `RUN_LIVE.bat`; enter your public GitHub login.
4. Review `output/summary.json` and the GIF. Live collection fails rather than silently falling back to demo figures.

PowerShell alternative after setting up Python:

```powershell
$env:PYTHONPATH = "src"
$env:GH_TOKEN = gh auth token
.venv\Scripts\python.exe -m gitrex live --login narayanangourav --output-dir output
Remove-Item Env:GH_TOKEN
```

You can also run `collect` and `render` separately:

```powershell
$env:PYTHONPATH = "src"
$env:GH_TOKEN = gh auth token
.venv\Scripts\python.exe -m gitrex collect --login narayanangourav --output snapshot.json
.venv\Scripts\python.exe -m gitrex render snapshot.json --output-dir output
Remove-Item Env:GH_TOKEN
```

`snapshot.json` is ignored in Git because it may contain personally identifiable activity metadata. The published `output/summary.json` contains only public-facing counts, the login, stage and inferred traits.

## GitHub profile integration

This project is designed for **a separate `GitRex` repository**. The daily workflow regenerates and commits assets in that repository. Add this to the `README.md` in your **profile repository** (for example `narayanangourav/narayanangourav`):

```markdown
## My GitRex

![My contribution-powered T-Rex](https://raw.githubusercontent.com/narayanangourav/GitRex/main/output/trex.gif)
```

See **[docs/PUBLISHING.md](docs/PUBLISHING.md)** for copyright checks, Git setup, secure Actions settings and first-live-run verification. The workflow has not been run on your actual GitHub account from this environment.

## Growth rules

| Contributions | Stage |
|---:|---|
| 0–49 | Hatchling |
| 50–199 | Juvenile |
| 200–499 | Subadult |
| 500–999 | Adult |
| 1000+ | Apex Rex |

Each contribution increases the scale until the 1000-contribution cap. The source is GitHub's GraphQL **contribution calendar**, **not a raw count of all commits**; it can include issues, pull requests, reviews, and more. A separate commit-contribution total is included for reference. Some GitHub contributions may not be counted by GitHub because of branch, author, and attribution rules.

Yesterday's completed UTC-day activity selects the motion mode (`idle`, `walk`, `roar`). All modes use light body movement and breathing of the same illustrated sprite. **This release does not have individually animated limbs or a moving jaw.** The top language is derived approximately from public owned repositories.

## Architecture

```text
GitRex/
├── .github/workflows/gitrex.yml   # nightly regeneration, manual trigger
├── assets/
│   ├── forest_original.png        # reproducible original background
│   ├── trex_original.png          # reproducible original foreground sprite
│   └── demo_snapshot.json         # invented sample data, clearly labeled
├── src/gitrex/
│   ├── github.py                  # API data collection
│   ├── model.py                   # deterministic growth/streak calculations
│   ├── render.py                  # layered GIF/PNG renderer
│   └── cli.py                     # commands
├── tools/prepare_illustration.py   # offline sprite extraction from bundled generated art
├── tools/generate_procedural_art.py  # entirely source-drawn fallback
├── tests/                        # offline Python tests
├── docs/PUBLISHING.md             # publication checklist
├── ASSET_PROVENANCE.md            # proof and licensing notes
├── LICENSE                        # MIT
├── OPEN_PREVIEW.html              # no-install local growth simulator
├── RUN_DEMO.bat / RUN_LIVE.bat     # Windows launch scripts
└── output/                       # example rendered animation
```

## Cost, privacy and limitations

- No server, paid AI image API, or private token in the repo is needed.
- GitHub Actions' standard runners are available without runner-minute charges for public repositories under current published terms; review GitHub's current usage policies before enabling other resources.
- Only public-facing contribution data is intended for published output. Local authenticated activity snapshots are ignored.
- GitHub Actions schedules are not guaranteed to run at exact times.
- Internet and authenticated GitHub API access are required for **live** operation; this could not be tested here.
- Read [ASSET_PROVENANCE.md](ASSET_PROVENANCE.md) before publishing. The primary illustrated art comes from a newly AI-generated GitRex image bundled in the package. A separate fully procedural art set is also included. Newly generated artwork cannot be guaranteed legally exclusive or free of resemblance claims.

\n
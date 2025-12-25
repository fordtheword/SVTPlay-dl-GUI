# SVTPlay-dl Web GUI

> Flask-based web interface for downloading videos from Swedish streaming services (SVT Play, TV4 Play).

## Session Start

**Read `PROJEKT-STATUS.md` first** to get current project state before doing any work.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.9+, Flask |
| Frontend | HTML5, Bootstrap 5, Vanilla JS |
| Video Tool | svtplay-dl (CLI), FFmpeg |
| Storage | JSON (profiles), File system (downloads) |

## Project Structure

```
svtplay-dl web gui/
├── app.py                  # Flask main application
├── svtplay_handler.py      # Core download logic (898 lines)
├── profile_manager.py      # Profile management
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Web UI template
├── static/
│   ├── css/style.css       # Custom styling
│   └── js/app.js           # Frontend logic
├── downloads/              # Downloaded files
├── profiles.json           # Saved user profiles
├── install.bat             # Windows installation
├── start.bat               # Windows startup
└── upgrade.bat             # Upgrade script
```

## Commands

```bash
# Installation (Windows)
install.bat

# Start server (Windows)
start.bat

# Manual start
python app.py

# Upgrade
upgrade.bat
# or: git pull && pip install -r requirements.txt
```

**Default URL:** http://localhost:5000

---

## Key Features

- **Single/Season/Batch downloads** from SVT Play & TV4 Play
- **TV4 Play token auth** for premium content
- **Parallel thumbnail fetching** (10x faster)
- **Profile saving** for recurring downloads
- **Quality selection** (1080p, 720p, 480p, best)
- **Subtitle downloading**
- **Web-based upgrade & restart**
- **Folder browser** for download locations

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/info` | Get video/series info |
| `POST /api/episodes` | List all episodes |
| `POST /api/scrape` | Scrape with thumbnails |
| `POST /api/download` | Download single episode |
| `POST /api/download/season` | Download entire season |
| `POST /api/download/batch` | Download multiple videos |
| `GET /api/downloads` | Get all download status |
| `GET /api/profiles` | Get saved profiles |
| `POST /api/system/upgrade` | Upgrade app |
| `POST /api/system/restart` | Restart server |

---

## File Boundaries

### Safe to Edit
- `app.py` — Flask routes and endpoints
- `svtplay_handler.py` — Download logic
- `profile_manager.py` — Profile operations
- `config.py` — Configuration
- `templates/index.html` — Web UI
- `static/js/app.js` — Frontend logic
- `static/css/style.css` — Styling

### Data Files (Don't Delete)
- `profiles.json` — User saved profiles
- `downloads/` — Downloaded videos

### Auto-Generated
- `venv/` — Virtual environment
- `__pycache__/` — Python cache

## Verification

Before completing any change:
- [ ] `python app.py` starts without errors
- [ ] Web UI loads at localhost:5000
- [ ] Test download works (use short video)
- [ ] Profile saving/loading works

---

## Interaction Rules

There are **TWO DISTINCT MODES**. Never confuse them.

### DISCUSS MODE (Default)
**This is the DEFAULT mode. Stay here until explicitly told to switch.**

In Discuss Mode, I can:
- Analyze problems
- Read files to understand code
- Explain how things work
- Present multiple solution options
- Answer questions

In Discuss Mode, I **CANNOT**:
- Create files
- Edit files
- Run commands that modify anything
- Implement solutions

**Key point:** When you describe what you want ("I'd like X"), we are **STILL IN DISCUSS MODE**. You're sharing your goal, NOT telling me to implement it.

### CODE MODE (Explicit Switch Required)

**Phrases that switch to Code Mode:**
- "Go ahead"
- "Do it"
- "Yes" / "Proceed"
- "Implement that"
- "Let's do option X"

**After completing the task, I return to Discuss Mode automatically.**

### Correct Workflow

1. **Analyze** the problem
2. **Present OPTIONS** (multiple approaches if possible)
3. **WAIT** for you to choose
4. **Ask for confirmation** before implementing
5. **ONLY THEN** make the change

### When in Doubt

**ASK. ALWAYS ASK.**

---

## Quick Reference

| Task | Where |
|------|-------|
| Add endpoint | `app.py` |
| Download logic | `svtplay_handler.py` |
| Profile storage | `profile_manager.py` |
| Configuration | `config.py` |
| UI changes | `templates/index.html` |
| Frontend logic | `static/js/app.js` |

## External Documentation

- **README.md** — Full installation & usage guide
- **QUICKSTART.md** — Quick start guide
- **IMPROVEMENTS_2025-11-08.md** — Recent improvements
- **TODO-QUEUE.md** — Feature backlog

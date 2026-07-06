# SVTPlay-dl Web GUI - Project Status

> Last updated: 2026-07-06

## Current Status

### What's Working
- Single episode download
- Season download (all episodes)
- Batch download (select multiple)
- Video browser with thumbnails
- TV4 Play token authentication
- Profile saving/loading
- Quality selection (1080p, 720p, 480p, best)
- Subtitle downloading
- Real-time download status
- Parallel thumbnail fetching (10x faster)
- Audio/video merge (.ts+.audio.ts, .mp4+.m4a)
- Web-based upgrade & restart
- Folder browser
- Last folder persistence
- Docker deployment (always-on via docker-compose)
- "Open download folder" button (opens Explorer locally, copies network path on Docker/NUC)

### Supported Services
- SVT Play (svtplay.se)
- TV4 Play (tv4play.se) with token auth

---

## In Progress

Nothing currently in progress.

---

## Pending Features (from TODO-QUEUE.md)

| Feature | Priority | Notes |
|---------|----------|-------|
| Persistent download queue | High | Queue lost on restart |
| Pause/resume downloads | Medium | Currently can only cancel |
| Download priority | Medium | All downloads equal priority |
| Automatic retry | Low | Failed downloads need manual retry |
| Thumbnail caching | Low | Re-fetched each time |
| Dark mode UI | Low | Currently light only |

---

## Key Decisions

| Decision | Reason | Date |
|----------|--------|------|
| Flask over Django | Lightweight, simple for this use case | Initial |
| svtplay-dl CLI over API | Reuse proven tool, active maintenance | Initial |
| JSON profiles over DB | Simple, no server needed | Initial |
| Parallel thumbnails | 10x speedup for browsing | 2025-11 |
| imageio-ffmpeg | Auto-install FFmpeg via pip | 2025-11 |
| Docker deployment | Always-on, downloads to D:\Torrents via mount | 2026-02 |
| Moved deployment to NUC | Container now runs on nucdocker, not local Windows Docker | 2026 |
| NETWORK_DOWNLOAD_PATH env var | "Open folder" button copies UNC path when server is remote | 2026-07 |

---

## Recent Changes (July 2026)

- "Open download folder" button (Öppna) next to the folder browser
- New endpoint POST /api/open-folder with tests (test_open_folder.py)
- NETWORK_DOWNLOAD_PATH env var: when set, the button copies the network
  path (\\192.168.1.72\torrents\downloads\svtplay) instead of opening a
  folder on the server
- Deployed to the NUC container (files copied + compose env var + rebuild)

## Changes (February 2026)

- Docker deployment with docker-compose (always-on, restart: unless-stopped)
- Nginx Proxy Manager integration (svtplay.local)
- Homepage dashboard entry
- Environment variable support for DOWNLOAD_DIR and PROFILES_FILE
- .dockerignore for clean builds

## Changes (November 2025)

- Parallel thumbnail fetching (10x speedup)
- Audio merge fix for .ts+.audio.ts and .mp4+.m4a
- Service-aware error messages (SVT vs TV4)
- Image display fix (proper fitting)
- Download folder persistence
- Automatic FFmpeg installation via pip
- Server restart from web UI

---

## Useful Commands

```bash
# Start server (local)
start.bat
# or: python app.py

# Start server (Docker, runs on the NUC)
ssh nuc "cd /home/adrian/docker/svtplay-dl && docker compose up -d"

# Deploy code changes to the NUC (no git on the NUC side — copy files, then rebuild)
scp app.py config.py nuc:/home/adrian/docker/svtplay-dl/
scp static/js/app.js nuc:/home/adrian/docker/svtplay-dl/static/js/
scp templates/index.html nuc:/home/adrian/docker/svtplay-dl/templates/
ssh nuc "cd /home/adrian/docker/svtplay-dl && docker compose up -d --build"

# Upgrade
upgrade.bat
# or: git pull && pip install -r requirements.txt

# Check versions
svtplay-dl --version
python --version
```

## Docker Setup

- **Host:** NUC (`ssh nuc`, 192.168.1.72) — NOT local Windows Docker
- **Container:** svtplay-dl (/home/adrian/docker/svtplay-dl/ on the NUC)
- **Deployment:** manual file copy (the folder is a snapshot, gitignored inside the
  NUC's docker repo — it is NOT a git clone of this repo)
- **URL:** http://svtplay.local or http://192.168.1.72:5052
- **Downloads:** /data/downloads/svtplay on the NUC (mounted as /downloads);
  reachable from Windows at \\192.168.1.72\torrents\downloads\svtplay
- **Profiles:** Docker volume (svtplay-profiles)
- **Network:** proxy-net (Nginx Proxy Manager)
- **Env vars:** DOWNLOAD_DIR, PROFILES_FILE, NETWORK_DOWNLOAD_PATH

---

## Notes for Next Session

- All core features working
- Running in Docker on the NUC (always-on) at svtplay.local / 192.168.1.72:5052
- Local working tree has an uncommitted svtplay_handler.py modification plus
  several untracked experiment files (svt_patch.py, test_scrape.py, etc.)
- Queue persistence is top priority for future
- Check TODO-QUEUE.md for detailed feature plans
- TV4 Play requires token (see UI for instructions)

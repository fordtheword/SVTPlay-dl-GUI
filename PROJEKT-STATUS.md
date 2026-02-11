# SVTPlay-dl Web GUI - Project Status

> Last updated: 2026-02-11

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

---

## Recent Changes (February 2026)

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

# Start server (Docker)
cd C:\docker\svtplay-dl && docker compose up -d

# Rebuild after code changes
cd C:\docker\svtplay-dl && docker compose up -d --build

# Upgrade
upgrade.bat
# or: git pull && pip install -r requirements.txt

# Check versions
svtplay-dl --version
python --version
```

## Docker Setup

- **Container:** svtplay-dl (C:\docker\svtplay-dl\)
- **URL:** http://svtplay.local or http://localhost:5052
- **Downloads:** D:\Torrents (mounted as /downloads)
- **Profiles:** Docker volume (svtplay-profiles)
- **Network:** proxy-net (Nginx Proxy Manager)

---

## Notes for Next Session

- All core features working
- Running in Docker (always-on) at svtplay.local
- Queue persistence is top priority for future
- Check TODO-QUEUE.md for detailed feature plans
- TV4 Play requires token (see UI for instructions)

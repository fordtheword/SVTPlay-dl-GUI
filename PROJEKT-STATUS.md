# SVTPlay-dl Web GUI - Project Status

> Last updated: 2025-12-25

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

---

## Recent Changes (November 2025)

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
# Start server
start.bat
# or: python app.py

# Upgrade
upgrade.bat
# or: git pull && pip install -r requirements.txt

# Check versions
svtplay-dl --version
python --version
```

---

## Notes for Next Session

- All core features working
- Queue persistence is top priority for future
- Check TODO-QUEUE.md for detailed feature plans
- TV4 Play requires token (see UI for instructions)

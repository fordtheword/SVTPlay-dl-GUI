# Modifications Made to SVTPlay-dl GUI

## Date: 2025-11-07

## Issue Fixed: Audio/Video Merge Problem

### Problem
When downloading videos from SVT Play, the system was creating separate files:
- `video-name.ts` (video only, no sound)
- `video-name.audio.ts` (audio only)
- `video-name.srt` (subtitles)

The automatic merging feature of svtplay-dl was not working, leaving users with video files without sound.

### Solution
Added automatic post-download FFmpeg merging to combine audio and video streams into a single MKV file.

---

## Changes Made

### 1. Fixed Unicode Console Output (`config.py`)
**File:** `config.py` (lines 36, 47, 55, 61-64)

**Change:** Replaced Unicode symbols (✓, ⚠) with ASCII alternatives to prevent Windows console encoding errors.

**Before:**
```python
print(f"✓ Using imageio-ffmpeg: {Config.FFMPEG_PATH}")
print("⚠ WARNING: ffmpeg not found!")
```

**After:**
```python
print(f"[OK] Using imageio-ffmpeg: {Config.FFMPEG_PATH}")
print("[WARNING] ffmpeg not found!")
```

---

### 2. Enhanced FFmpeg PATH Setup (`svtplay_handler.py`)
**File:** `svtplay_handler.py` (lines 39-54)

**Change:** Modified `get_env_with_local_bin()` function to add FFmpeg directory to PATH environment variable.

**Added:**
```python
# Add FFmpeg from imageio-ffmpeg or Config.FFMPEG_PATH to PATH
if Config.FFMPEG_PATH:
    ffmpeg_dir = os.path.dirname(Config.FFMPEG_PATH)
    if ffmpeg_dir and os.path.exists(ffmpeg_dir):
        env['PATH'] = ffmpeg_dir + os.pathsep + env.get('PATH', '')
```

**Why:** Ensures svtplay-dl can find FFmpeg for merging operations.

---

### 3. Added Automatic Audio/Video Merging (`svtplay_handler.py`)
**File:** `svtplay_handler.py` (lines 321-323, 467-469, 526-578)

**Change:** Added `_merge_audio_video_if_needed()` method that runs after each download completes.

**Method Added:**
```python
def _merge_audio_video_if_needed(self, download_dir):
    """Merge separate audio and video .ts files into one .mkv file using FFmpeg"""
    # Finds .ts and .audio.ts file pairs
    # Merges them using FFmpeg with -c copy (no re-encoding)
    # Deletes original separate files after successful merge
```

**Integration Points:**
- Called after single downloads complete (line 323)
- Called after season downloads complete (line 469)

**How it works:**
1. Scans download directory for `.ts` files
2. For each video file, checks if matching `.audio.ts` exists
3. If both exist, runs FFmpeg to merge:
   ```
   ffmpeg -i video.ts -i video.audio.ts -c copy -y output.mkv
   ```
4. Deletes original `.ts` and `.audio.ts` files after successful merge
5. Keeps `.srt` subtitle files intact

---

## FFmpeg Configuration

### FFmpeg Location
The system uses FFmpeg from `imageio-ffmpeg` package installed via pip:
```
venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe
```

### Fallback Options
If imageio-ffmpeg is not available, the system checks:
1. Local `bin/ffmpeg.exe` in project directory
2. System PATH for ffmpeg command

---

## Result

### Before Modifications
After download completed:
```
video-name.ts           (video only - NO SOUND)
video-name.audio.ts     (audio only)
video-name.srt          (subtitles)
```

### After Modifications
After download completes:
```
video-name.mkv          (merged video + audio - WITH SOUND)
video-name.srt          (subtitles)
```

The separate `.ts` files are automatically deleted after successful merge.

---

## Files Modified

1. **config.py** - Fixed Unicode output for Windows console
2. **svtplay_handler.py** - Added FFmpeg PATH setup and automatic merge function

## Testing

Tested with:
- URL: https://www.svtplay.se/video/ePvLMgQ/sisu
- Result: Successfully merged 2.2GB MKV file with audio and video
- Playback: Confirmed audio working in VLC Media Player

---

## Technical Details

### Merge Command
```bash
ffmpeg -i video.ts -i audio.ts -c copy -y output.mkv
```

**Flags:**
- `-i video.ts` - Input video stream
- `-i audio.ts` - Input audio stream
- `-c copy` - Copy streams without re-encoding (fast, no quality loss)
- `-y` - Overwrite output file if exists
- `output.mkv` - Output file in MKV container format

### Performance
- Merge is very fast (uses stream copy, no transcoding)
- Example: 2.2GB file merged in ~3 seconds
- No quality loss (streams copied bit-for-bit)

---

## Maintenance Notes

- Merge happens automatically after each download
- No user intervention required
- Merge failures are logged to console but don't stop the download process
- Original files only deleted after successful merge

---

## Future Improvements (Optional)

Potential enhancements if needed:
1. Add user option to choose output format (MKV, MP4, etc.)
2. Add progress indicator for merge operation in web UI
3. Add option to keep original separate files
4. Add batch merge tool for existing separate files

---

Generated: 2025-11-07
Modified by: Claude (Anthropic AI Assistant)
Original Project: https://github.com/andersmolausson/SVTPlay-dl-GUI

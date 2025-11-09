# Download Queue System - Implementation Plan

## Date: 2025-11-07
## Status: PLANNED FOR IMPLEMENTATION

---

## 📌 Additional Feature: Download Folder Persistence

### Date: 2025-11-09
### Status: TO BE IMPLEMENTED
### Priority: Low (Quality of Life)

**Feature Request:**
The "Nedladdningsmapp" (Download folder) field should remember the last folder path used across server restarts.

**Current Behavior:**
- Field is empty on each page load/server restart
- User must re-enter or browse for folder each time (unless using saved profiles)

**Desired Behavior:**
- Field remembers last used folder path
- Auto-fills when page loads
- Persists across server restarts

**Implementation Approach:**
1. Store last used folder path in a persistence file (options):
   - Add to existing `profiles.json` as a top-level field (e.g., `"last_download_folder": "D:\\TV-Serier"`)
   - OR create new `user_preferences.json` for this and future user preferences
2. Backend changes:
   - Modify download endpoints to save folder path when used
   - Add GET endpoint to retrieve last used folder (e.g., `/api/preferences/last-folder`)
3. Frontend changes:
   - On page load, fetch last used folder and populate the field
   - Update field whenever user changes folder (browse or manual entry)

**Files to Modify:**
- `app.py` - Add preference endpoints
- `static/js/app.js` - Auto-populate folder field on page load
- `profiles.json` or new `user_preferences.json` - Store the value

**Estimated Effort:** 30 minutes - 1 hour

---

## Overview

Add a comprehensive download queue management system to the SVTPlay-dl GUI, allowing users to:
- View all downloads in a single organized list
- Manage download priority and order
- Pause/resume/cancel downloads
- Retry failed downloads
- See real-time status updates

---

## Current System

### Existing Functionality
- Concurrent downloads: 3 simultaneous downloads (hardcoded in `config.py`)
- Download tracking: Basic status stored in memory (`svtplay_handler.py`)
- UI polling: Frontend polls `/api/downloads` every 5 seconds
- No persistent queue or priority management

### Current Status Display
```
Downloads shown individually with:
- ID (UUID)
- URL
- Status (queued/downloading/completed/failed)
- Progress percentage
- Start/finish timestamps
- Error messages
```

---

## Planned Features

### 1. Visual Queue List
**Location:** Main page of web UI

**Display:**
```
┌─────────────────────────────────────────────────────────┐
│ Download Queue (4 active, 2 waiting, 3 completed)       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 🟢 DOWNLOADING                                          │
│ ⬇️ Sisu (2025)                          [████░░] 65%    │
│    Started: 23:01  •  ETA: 2 min  •  2.2 GB             │
│    [Pause] [Cancel]                                      │
│                                                          │
│ ⬇️ Vikings S01E01                       [██░░░░] 35%    │
│    Started: 23:00  •  ETA: 5 min  •  1.5 GB             │
│    [Pause] [Cancel]                                      │
│                                                          │
│ 🟡 WAITING                                               │
│ ⏳ Vikings S01E02                                        │
│    Position: 3 in queue                                  │
│    [Move Up] [Move Down] [Cancel]                        │
│                                                          │
│ ⏳ Vikings S01E03                                        │
│    Position: 4 in queue                                  │
│    [Move Up] [Move Down] [Cancel]                        │
│                                                          │
│ ⏸️ PAUSED                                                │
│ ⏸️ Another Movie                        [███░░░] 50%    │
│    Paused at: 22:55                                      │
│    [Resume] [Cancel]                                     │
│                                                          │
│ ✅ COMPLETED                                             │
│ ✓ Documentary                                            │
│    Finished: 22:50  •  Size: 3.1 GB                      │
│    📁 C:\Users\...\Downloads\documentary.mkv             │
│    [Open Folder] [Play]                                  │
│                                                          │
│ ❌ FAILED                                                │
│ ✗ Some Series                                            │
│    Error: Token required or expired                      │
│    [Retry] [Remove]                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

### 2. Queue Management Actions

#### Pause/Resume
- **Pause:** Stop current download, save progress state
- **Resume:** Continue from where it left off
- Implementation: Kill process, save state, restart with same parameters

#### Cancel
- **Action:** Stop download and remove from queue
- **Cleanup:** Delete partial files
- **Confirmation:** "Are you sure?" dialog

#### Move Up/Down
- **Action:** Change priority in waiting queue
- **Effect:** Higher priority downloads start first
- **Limitation:** Can't reorder active downloads

#### Retry
- **Action:** Re-queue failed download with same parameters
- **Auto-retry:** Optional - retry failed downloads automatically (3 attempts)

#### Remove Completed
- **Action:** Clear completed/failed downloads from list
- **Keep history:** Optional - save to download history file

---

### 3. Multi-URL Queue Addition

**Feature:** Add multiple URLs at once, auto-queue them

**UI Addition:**
```
┌─ Add to Queue ───────────────────┐
│                                   │
│ Paste URLs (one per line):       │
│ ┌───────────────────────────────┐ │
│ │ https://svtplay.se/video/...  │ │
│ │ https://svtplay.se/video/...  │ │
│ │ https://svtplay.se/video/...  │ │
│ │                               │ │
│ └───────────────────────────────┘ │
│                                   │
│ Download Settings:                │
│ ☑ Use same settings for all      │
│ Quality: [Best ▼]                 │
│ Location: [...Browse]             │
│                                   │
│ [Add 3 Downloads to Queue]        │
│                                   │
└───────────────────────────────────┘
```

---

### 4. Queue Persistence

**Save queue to disk:**
- File: `queue.json` in project root
- Save on changes
- Load on server start
- Resume interrupted downloads

**Queue data structure:**
```json
{
  "queue_version": "1.0",
  "last_updated": "2025-11-07T23:15:00",
  "downloads": [
    {
      "id": "uuid-here",
      "url": "https://...",
      "status": "paused",
      "priority": 1,
      "progress": 50,
      "options": {
        "quality": "best",
        "download_dir": "C:\\Users\\...",
        "subtitle": true
      },
      "metadata": {
        "title": "Video Title",
        "added_at": "2025-11-07T23:00:00",
        "started_at": "2025-11-07T23:01:00",
        "paused_at": "2025-11-07T23:05:00",
        "file_size": 2200000000
      }
    }
  ]
}
```

---

### 5. Queue Statistics

**Display at top of queue:**
```
Queue Summary:
- Active: 2 downloading
- Waiting: 3 queued
- Paused: 1 paused
- Completed today: 5 (12.3 GB)
- Failed: 1
- Estimated time remaining: 15 minutes
```

---

## Technical Implementation

### Backend Changes

#### 1. Queue Manager Class (`svtplay_handler.py`)
```python
class QueueManager:
    def __init__(self):
        self.queue = []  # Ordered list of downloads
        self.load_queue()

    def add_to_queue(self, url, options, priority=None):
        """Add download to queue"""

    def remove_from_queue(self, download_id):
        """Remove download from queue"""

    def move_in_queue(self, download_id, direction):
        """Move up or down in queue"""

    def pause_download(self, download_id):
        """Pause active download"""

    def resume_download(self, download_id):
        """Resume paused download"""

    def get_queue_status(self):
        """Get full queue with stats"""

    def save_queue(self):
        """Persist queue to disk"""

    def load_queue(self):
        """Load queue from disk"""
```

#### 2. New API Endpoints (`app.py`)
```python
@app.route('/api/queue', methods=['GET'])
def get_queue():
    """Get full queue with all downloads"""

@app.route('/api/queue/add', methods=['POST'])
def add_to_queue():
    """Add single or multiple URLs to queue"""

@app.route('/api/queue/<download_id>/pause', methods=['POST'])
def pause_download():
    """Pause a download"""

@app.route('/api/queue/<download_id>/resume', methods=['POST'])
def resume_download():
    """Resume a paused download"""

@app.route('/api/queue/<download_id>/cancel', methods=['POST'])
def cancel_download():
    """Cancel and remove download"""

@app.route('/api/queue/<download_id>/move', methods=['POST'])
def move_in_queue():
    """Move download up/down in queue"""
    # POST data: {"direction": "up" or "down"}

@app.route('/api/queue/<download_id>/retry', methods=['POST'])
def retry_download():
    """Retry a failed download"""

@app.route('/api/queue/cleanup', methods=['POST'])
def cleanup_queue():
    """Remove completed/failed downloads"""
```

#### 3. Download State Management
```python
DOWNLOAD_STATES = {
    'queued': 'Waiting in queue',
    'downloading': 'Downloading',
    'paused': 'Paused by user',
    'merging': 'Merging audio/video',
    'completed': 'Download completed',
    'failed': 'Download failed',
    'cancelled': 'Cancelled by user'
}
```

### Frontend Changes

#### 1. Queue Component (`templates/index.html` or new `queue.html`)
- Separate sections for each status
- Collapsible sections
- Real-time updates via polling or WebSockets
- Drag-and-drop reordering (optional)

#### 2. Queue Actions (`static/js/app.js`)
```javascript
// Queue management functions
function pauseDownload(downloadId) { ... }
function resumeDownload(downloadId) { ... }
function cancelDownload(downloadId) { ... }
function moveInQueue(downloadId, direction) { ... }
function retryDownload(downloadId) { ... }
function addMultipleToQueue(urls, options) { ... }
function updateQueueDisplay() { ... }
```

#### 3. UI Updates
- Add "Queue" tab or section
- Add bulk URL input area
- Add queue statistics dashboard
- Add filter/sort options (by status, date, size)

---

## Configuration Options

### New Config Settings (`config.py`)
```python
# Queue settings
MAX_CONCURRENT_DOWNLOADS = 3  # Already exists
MAX_QUEUE_SIZE = 100  # Maximum items in queue
AUTO_RETRY_FAILED = True  # Automatically retry failed downloads
MAX_RETRY_ATTEMPTS = 3  # How many times to retry
QUEUE_PERSISTENCE = True  # Save queue to disk
CLEANUP_ON_COMPLETE = False  # Auto-remove completed downloads
PAUSE_ON_ERROR = True  # Pause queue if download fails
```

---

## User Workflows

### Workflow 1: Add Multiple Downloads
1. User pastes 10 URLs into bulk input
2. Sets quality and download location
3. Clicks "Add to Queue"
4. All 10 are queued, 3 start immediately
5. Others wait in queue

### Workflow 2: Manage Priority
1. User sees Vikings S01E03 in queue
2. Wants to watch it first
3. Clicks "Move Up" twice
4. Episode moves to position 1
5. Starts downloading after current batch

### Workflow 3: Pause and Resume
1. Download in progress
2. User needs bandwidth for video call
3. Clicks "Pause"
4. Download stops, saves state
5. Later clicks "Resume"
6. Download continues from 50%

### Workflow 4: Handle Failure
1. Download fails (token expired)
2. Shows in "Failed" section with error
3. User fixes token issue
4. Clicks "Retry"
5. Download re-queues and starts

---

## Phase 1: Core Queue (Tomorrow)

**Priority Features:**
1. ✅ Display all downloads in organized list
2. ✅ Pause/resume functionality
3. ✅ Cancel/remove downloads
4. ✅ Queue reordering (move up/down)
5. ✅ Retry failed downloads
6. ✅ Queue persistence (save/load)

**Skip for Phase 1:**
- Drag-and-drop reordering
- WebSocket real-time updates
- Download history database
- Advanced filtering/sorting

---

## Phase 2: Enhancements (Future)

**Nice-to-Have Features:**
1. Drag-and-drop reordering
2. WebSocket for instant updates (no polling)
3. Download history with search
4. Queue templates (save frequent download configs)
5. Scheduled downloads (start at specific time)
6. Speed limiting per download
7. Download categories/tags
8. Export queue to file

---

## Testing Plan

### Test Cases
1. Add single download → verify queues correctly
2. Add 10 downloads → verify only 3 run concurrently
3. Pause active download → verify saves state
4. Resume paused → verify continues from same point
5. Cancel mid-download → verify cleanup
6. Move queued item up → verify priority changes
7. Retry failed download → verify re-queues
8. Server restart → verify queue persists
9. Complete download → verify merging still works
10. Fill queue to max → verify limit enforced

---

## Files to Modify

1. **svtplay_handler.py** - Add QueueManager class
2. **app.py** - Add new queue API endpoints
3. **templates/index.html** - Add queue UI components
4. **static/js/app.js** - Add queue management JavaScript
5. **static/css/style.css** - Style queue interface
6. **config.py** - Add queue configuration options

---

## Estimated Effort

- Backend (QueueManager + API): 2-3 hours
- Frontend (UI + JavaScript): 2-3 hours
- Testing + bug fixes: 1-2 hours
- **Total: 5-8 hours**

---

## Success Criteria

✅ User can add multiple downloads at once
✅ Downloads queue automatically when concurrent limit reached
✅ User can pause/resume any download
✅ User can reorder waiting downloads
✅ Queue persists across server restarts
✅ Failed downloads can be retried
✅ UI clearly shows download status and progress
✅ Queue statistics displayed accurately

---

## Notes

- Keep existing single-download functionality working
- Queue is optional - users can still do one-off downloads
- Preserve all current features (profiles, folder browser, etc.)
- Don't break the auto-merge functionality we just added

---

Ready to implement tomorrow! 🚀

Generated: 2025-11-07
Plan by: Claude (Anthropic AI Assistant)

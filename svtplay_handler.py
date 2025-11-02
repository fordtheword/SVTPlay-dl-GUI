import subprocess
import json
import os
import threading
import queue
from datetime import datetime
from config import Config

class SVTPlayDownloader:
    """Handles downloads using svtplay-dl"""

    def __init__(self):
        self.downloads = {}  # Store download status {id: {...}}
        self.download_queue = queue.Queue()
        self.active_downloads = 0
        self.max_concurrent = Config.MAX_CONCURRENT_DOWNLOADS

    def get_info(self, url):
        """Get information about a video or series without downloading"""
        try:
            cmd = ['svtplay-dl', '--json-info', url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                # Parse the JSON output
                info = json.loads(result.stdout)
                return {
                    'success': True,
                    'info': info
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr or 'Failed to get video information'
                }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Request timed out'}
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Failed to parse video information'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_episodes(self, url):
        """List all episodes from a series URL"""
        try:
            cmd = ['svtplay-dl', '--list-episodes', url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                episodes = []
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if line and line.startswith('http'):
                        episodes.append(line)
                return {
                    'success': True,
                    'episodes': episodes,
                    'count': len(episodes)
                }
            else:
                return {'success': False, 'error': result.stderr or 'Failed to list episodes'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def start_download(self, url, options=None):
        """Start a download task"""
        download_id = self._generate_id()

        self.downloads[download_id] = {
            'id': download_id,
            'url': url,
            'status': 'queued',
            'progress': 0,
            'message': 'Queued for download',
            'started_at': datetime.now().isoformat(),
            'finished_at': None,
            'error': None,
            'output_file': None
        }

        # Start download in a separate thread
        thread = threading.Thread(
            target=self._download_worker,
            args=(download_id, url, options)
        )
        thread.daemon = True
        thread.start()

        return {'success': True, 'download_id': download_id}

    def _download_worker(self, download_id, url, options):
        """Worker thread for downloading"""
        try:
            self.downloads[download_id]['status'] = 'downloading'
            self.downloads[download_id]['message'] = 'Downloading...'

            # Build command
            cmd = ['svtplay-dl']

            # Add quality option
            quality = options.get('quality', Config.DEFAULT_QUALITY) if options else Config.DEFAULT_QUALITY
            cmd.extend(['-q', quality])

            # Add subtitle option
            if options and options.get('subtitle', Config.DEFAULT_SUBTITLE):
                cmd.append('--subtitle')

            # Add output directory
            cmd.extend(['-o', os.path.join(Config.DOWNLOAD_DIR, '%(title)s_%(episodename)s.%(ext)s')])

            # Add URL
            cmd.append(url)

            # Run download
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Read output
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self.downloads[download_id]['status'] = 'completed'
                self.downloads[download_id]['message'] = 'Download completed'
                self.downloads[download_id]['progress'] = 100
                self.downloads[download_id]['finished_at'] = datetime.now().isoformat()
            else:
                self.downloads[download_id]['status'] = 'failed'
                self.downloads[download_id]['message'] = 'Download failed'
                self.downloads[download_id]['error'] = stderr or 'Unknown error'
                self.downloads[download_id]['finished_at'] = datetime.now().isoformat()

        except Exception as e:
            self.downloads[download_id]['status'] = 'failed'
            self.downloads[download_id]['message'] = 'Download failed'
            self.downloads[download_id]['error'] = str(e)
            self.downloads[download_id]['finished_at'] = datetime.now().isoformat()

    def download_season(self, url, options=None):
        """Download entire season/series"""
        download_id = self._generate_id()

        self.downloads[download_id] = {
            'id': download_id,
            'url': url,
            'status': 'queued',
            'progress': 0,
            'message': 'Queued for season download',
            'started_at': datetime.now().isoformat(),
            'finished_at': None,
            'error': None,
            'type': 'season'
        }

        # Start download in a separate thread
        thread = threading.Thread(
            target=self._season_download_worker,
            args=(download_id, url, options)
        )
        thread.daemon = True
        thread.start()

        return {'success': True, 'download_id': download_id}

    def _season_download_worker(self, download_id, url, options):
        """Worker thread for downloading entire season"""
        try:
            self.downloads[download_id]['status'] = 'downloading'
            self.downloads[download_id]['message'] = 'Downloading season...'

            # Build command
            cmd = ['svtplay-dl']

            # Add all episodes flag
            cmd.append('--all-episodes')

            # Add quality option
            quality = options.get('quality', Config.DEFAULT_QUALITY) if options else Config.DEFAULT_QUALITY
            cmd.extend(['-q', quality])

            # Add subtitle option
            if options and options.get('subtitle', Config.DEFAULT_SUBTITLE):
                cmd.append('--subtitle')

            # Add output directory
            cmd.extend(['-o', os.path.join(Config.DOWNLOAD_DIR, '%(title)s_S%(season)sE%(episode)s_%(episodename)s.%(ext)s')])

            # Add URL
            cmd.append(url)

            # Run download
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Read output
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self.downloads[download_id]['status'] = 'completed'
                self.downloads[download_id]['message'] = 'Season download completed'
                self.downloads[download_id]['progress'] = 100
                self.downloads[download_id]['finished_at'] = datetime.now().isoformat()
            else:
                self.downloads[download_id]['status'] = 'failed'
                self.downloads[download_id]['message'] = 'Season download failed'
                self.downloads[download_id]['error'] = stderr or 'Unknown error'
                self.downloads[download_id]['finished_at'] = datetime.now().isoformat()

        except Exception as e:
            self.downloads[download_id]['status'] = 'failed'
            self.downloads[download_id]['message'] = 'Season download failed'
            self.downloads[download_id]['error'] = str(e)
            self.downloads[download_id]['finished_at'] = datetime.now().isoformat()

    def get_status(self, download_id):
        """Get status of a specific download"""
        if download_id in self.downloads:
            return {'success': True, 'download': self.downloads[download_id]}
        else:
            return {'success': False, 'error': 'Download not found'}

    def get_all_downloads(self):
        """Get all downloads"""
        return {
            'success': True,
            'downloads': list(self.downloads.values())
        }

    def _generate_id(self):
        """Generate a unique download ID"""
        import uuid
        return str(uuid.uuid4())

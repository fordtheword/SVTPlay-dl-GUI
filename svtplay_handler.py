import subprocess
import json
import os
import sys
import threading
import queue
import re
from datetime import datetime
from config import Config

# Get the path to svtplay-dl in the virtual environment
def get_svtplay_dl_command():
    """Get the correct command to run svtplay-dl - returns a list"""
    # If running in a virtual environment, use that path
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        venv_path = sys.prefix
        if os.name == 'nt':  # Windows
            svtplay_exe = os.path.join(venv_path, 'Scripts', 'svtplay-dl.exe')
            # Check if .exe exists
            if os.path.exists(svtplay_exe):
                return [svtplay_exe]
            # Fallback to Python module
            python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
            return [python_exe, '-m', 'svtplay_dl']
        else:  # Unix/Linux/Mac
            svtplay_path = os.path.join(venv_path, 'bin', 'svtplay-dl')
            if os.path.exists(svtplay_path):
                return [svtplay_path]
            # Fallback to Python module
            python_path = os.path.join(venv_path, 'bin', 'python')
            return [python_path, '-m', 'svtplay_dl']

    # Fallback to just 'svtplay-dl' (will use PATH)
    return ['svtplay-dl']

SVTPLAY_DL_CMD = get_svtplay_dl_command()

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
            cmd = SVTPLAY_DL_CMD + ['--json-info', url]
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
            cmd = SVTPLAY_DL_CMD + ['--list-episodes', url]
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

    def _process_output_realtime(self, process, download_id):
        """
        Process svtplay-dl output in real-time and update download status.
        Parses episode information and tracks progress.
        Returns: (stdout_lines, stderr_lines, full_output)
        """
        stdout_lines = []
        stderr_lines = []

        # Regular expressions for parsing
        episode_pattern = re.compile(r'Episode\s+(\d+)\s+of\s+(\d+)', re.IGNORECASE)
        url_pattern = re.compile(r'Url:\s+(https?://[^\s]+)', re.IGNORECASE)
        outfile_pattern = re.compile(r'Outfile:\s+(.+)', re.IGNORECASE)
        exists_pattern = re.compile(r'already exists', re.IGNORECASE)
        downloading_pattern = re.compile(r'downloading', re.IGNORECASE)

        current_episode = None
        episodes = {}  # Store episode data

        # Read stderr in real-time (svtplay-dl writes most info to stderr)
        for line in iter(process.stderr.readline, ''):
            if not line:
                break

            line = line.strip()
            stderr_lines.append(line)

            # Parse episode number
            episode_match = episode_pattern.search(line)
            if episode_match:
                ep_num = int(episode_match.group(1))
                total = int(episode_match.group(2))
                current_episode = ep_num

                # Initialize episode entry
                if ep_num not in episodes:
                    episodes[ep_num] = {
                        'number': ep_num,
                        'total': total,
                        'status': 'processing',
                        'url': None,
                        'filename': None,
                        'skipped': False
                    }

                # Update download object with episodes list
                if 'episodes' not in self.downloads[download_id]:
                    self.downloads[download_id]['episodes'] = {}
                    self.downloads[download_id]['total_episodes'] = total
                    self.downloads[download_id]['completed_episodes'] = 0
                    self.downloads[download_id]['skipped_episodes'] = 0

                self.downloads[download_id]['episodes'][ep_num] = episodes[ep_num]
                self.downloads[download_id]['current_episode'] = ep_num
                self.downloads[download_id]['message'] = f'Processing episode {ep_num} of {total}'

            # Parse URL
            if current_episode and url_pattern.search(line):
                url_match = url_pattern.search(line)
                episodes[current_episode]['url'] = url_match.group(1)
                self.downloads[download_id]['episodes'][current_episode] = episodes[current_episode]

            # Parse outfile
            if current_episode and outfile_pattern.search(line):
                outfile_match = outfile_pattern.search(line)
                episodes[current_episode]['filename'] = outfile_match.group(1)
                self.downloads[download_id]['episodes'][current_episode] = episodes[current_episode]

            # Check if file already exists
            if current_episode and exists_pattern.search(line):
                episodes[current_episode]['status'] = 'skipped'
                episodes[current_episode]['skipped'] = True
                self.downloads[download_id]['episodes'][current_episode] = episodes[current_episode]
                self.downloads[download_id]['skipped_episodes'] = self.downloads[download_id].get('skipped_episodes', 0) + 1

            # Check if downloading
            if current_episode and downloading_pattern.search(line):
                episodes[current_episode]['status'] = 'downloading'
                self.downloads[download_id]['episodes'][current_episode] = episodes[current_episode]

        # Mark episodes as completed if they were being downloaded
        for ep_num, ep_data in episodes.items():
            if ep_data['status'] == 'downloading':
                ep_data['status'] = 'completed'
                self.downloads[download_id]['episodes'][ep_num] = ep_data
                self.downloads[download_id]['completed_episodes'] = self.downloads[download_id].get('completed_episodes', 0) + 1

        # Read any remaining stdout
        stdout_text = process.stdout.read()
        if stdout_text:
            stdout_lines = stdout_text.strip().split('\n')

        # Wait for process to finish
        process.wait()

        # Combine outputs
        full_output = '\n'.join(stdout_lines) + '\n' + '\n'.join(stderr_lines)

        return stdout_lines, stderr_lines, full_output

    def start_download(self, url, options=None):
        """Start a download task"""
        download_id = self._generate_id()

        # Get custom download directory if provided
        download_dir = options.get('download_dir', Config.DOWNLOAD_DIR) if options else Config.DOWNLOAD_DIR

        self.downloads[download_id] = {
            'id': download_id,
            'url': url,
            'status': 'queued',
            'progress': 0,
            'message': 'Queued for download',
            'started_at': datetime.now().isoformat(),
            'finished_at': None,
            'error': None,
            'output_file': None,
            'download_dir': download_dir
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

            # Get custom download directory if provided
            download_dir = options.get('download_dir', Config.DOWNLOAD_DIR) if options else Config.DOWNLOAD_DIR

            # Ensure download directory exists
            os.makedirs(download_dir, exist_ok=True)

            # Build command
            cmd = SVTPLAY_DL_CMD.copy()

            # Add quality option - fix format for TV4 Play compatibility
            quality = options.get('quality', Config.DEFAULT_QUALITY) if options else Config.DEFAULT_QUALITY

            # TV4 Play doesn't accept "p" suffix (e.g., "480p"), only numbers or "best"
            # Remove "p" suffix if present
            if quality and quality != 'best':
                quality = quality.replace('p', '')

            # Only add quality parameter if not "best" - let svtplay-dl choose automatically for best
            if quality and quality != 'best':
                cmd.extend(['-q', quality])

            # Add subtitle option
            if options and options.get('subtitle', Config.DEFAULT_SUBTITLE):
                cmd.append('--subtitle')

            # Add token if provided (for TV4 Play and premium content)
            if options and options.get('token'):
                cmd.extend(['--token', options.get('token')])

            # Add output directory - let svtplay-dl use its default naming
            # Just ensure we run from the correct directory
            cmd.extend(['-o', download_dir + os.sep])

            # Add URL
            cmd.append(url)

            # Debug: Print the command being run
            print("=" * 80)
            print("DEBUG: Running svtplay-dl command (single download):")
            print(" ".join(cmd))
            print("=" * 80)

            # Run download
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Read output
            stdout, stderr = process.communicate()

            # Debug: Print output
            print("=" * 80)
            print("DEBUG: svtplay-dl output (single download):")
            print("STDOUT:", stdout[:1000] if stdout else "(empty)")
            print("STDERR:", stderr[:1000] if stderr else "(empty)")
            print("Return code:", process.returncode)
            print("=" * 80)

            # Combine stdout and stderr for better error detection
            full_output = (stdout or '') + '\n' + (stderr or '')

            # Check for specific error conditions
            token_required = 'token' in full_output.lower() and ('need' in full_output.lower() or 'require' in full_output.lower())
            no_videos_found = 'no videos found' in full_output.lower()
            drm_protected = 'drm' in full_output.lower() and 'protected' in full_output.lower()

            # Determine if download actually succeeded
            success = process.returncode == 0 and not token_required and not no_videos_found

            if success:
                self.downloads[download_id]['status'] = 'completed'
                self.downloads[download_id]['message'] = 'Download completed'
                self.downloads[download_id]['progress'] = 100
                self.downloads[download_id]['finished_at'] = datetime.now().isoformat()
            else:
                self.downloads[download_id]['status'] = 'failed'

                # Provide specific error messages
                if token_required:
                    self.downloads[download_id]['message'] = 'Token required or expired'
                    self.downloads[download_id]['error'] = 'This content requires a valid TV4 Play token. Please check that you have entered a token and that it has not expired. Click the "?" button next to the Token field for instructions.'
                elif no_videos_found:
                    self.downloads[download_id]['message'] = 'No videos found'
                    self.downloads[download_id]['error'] = 'No videos were found at this URL. Please check the URL or try logging in to TV4 Play and refreshing your token.'
                elif drm_protected:
                    self.downloads[download_id]['message'] = 'DRM protected content'
                    self.downloads[download_id]['error'] = 'This content is DRM protected and cannot be downloaded.'
                else:
                    self.downloads[download_id]['message'] = 'Download failed'
                    self.downloads[download_id]['error'] = stderr or stdout or 'Unknown error'

                self.downloads[download_id]['finished_at'] = datetime.now().isoformat()

        except Exception as e:
            self.downloads[download_id]['status'] = 'failed'
            self.downloads[download_id]['message'] = 'Download failed'
            self.downloads[download_id]['error'] = str(e)
            self.downloads[download_id]['finished_at'] = datetime.now().isoformat()

    def download_season(self, url, options=None):
        """Download entire season/series"""
        download_id = self._generate_id()

        # Get custom download directory if provided
        download_dir = options.get('download_dir', Config.DOWNLOAD_DIR) if options else Config.DOWNLOAD_DIR

        self.downloads[download_id] = {
            'id': download_id,
            'url': url,
            'status': 'queued',
            'progress': 0,
            'message': 'Queued for season download',
            'started_at': datetime.now().isoformat(),
            'finished_at': None,
            'error': None,
            'type': 'season',
            'download_dir': download_dir
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

            # Get custom download directory if provided
            download_dir = options.get('download_dir', Config.DOWNLOAD_DIR) if options else Config.DOWNLOAD_DIR

            # Ensure download directory exists
            os.makedirs(download_dir, exist_ok=True)

            # Build command
            cmd = SVTPLAY_DL_CMD.copy()

            # Add all episodes flag
            cmd.append('--all-episodes')

            # Add quality option - fix format for TV4 Play compatibility
            quality = options.get('quality', Config.DEFAULT_QUALITY) if options else Config.DEFAULT_QUALITY

            # TV4 Play doesn't accept "p" suffix (e.g., "480p"), only numbers or "best"
            # Remove "p" suffix if present
            if quality and quality != 'best':
                quality = quality.replace('p', '')

            # Only add quality parameter if not "best" - let svtplay-dl choose automatically for best
            if quality and quality != 'best':
                cmd.extend(['-q', quality])

            # Add subtitle option
            if options and options.get('subtitle', Config.DEFAULT_SUBTITLE):
                cmd.append('--subtitle')

            # Add token if provided (for TV4 Play and premium content)
            if options and options.get('token'):
                cmd.extend(['--token', options.get('token')])

            # Add output directory - let svtplay-dl use its default naming for seasons
            cmd.extend(['-o', download_dir + os.sep])

            # Add URL
            cmd.append(url)

            # Debug: Print the command being run
            print("=" * 80)
            print("DEBUG: Running svtplay-dl command (season download):")
            print(" ".join(cmd))
            print("=" * 80)

            # Run download
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered for real-time reading
            )

            # Process output in real-time and update episode status
            stdout_lines, stderr_lines, full_output = self._process_output_realtime(process, download_id)

            # Debug: Print summary
            print("=" * 80)
            print("DEBUG: svtplay-dl output (season download):")
            stderr_preview = '\n'.join(stderr_lines[:20]) if stderr_lines else "(empty)"
            print("STDERR (first 20 lines):", stderr_preview)
            print("Return code:", process.returncode)
            if 'total_episodes' in self.downloads[download_id]:
                print(f"Episodes processed: {self.downloads[download_id].get('total_episodes', 0)}")
                print(f"Completed: {self.downloads[download_id].get('completed_episodes', 0)}")
                print(f"Skipped: {self.downloads[download_id].get('skipped_episodes', 0)}")
            print("=" * 80)

            # Check for specific error conditions
            token_required = 'token' in full_output.lower() and ('need' in full_output.lower() or 'require' in full_output.lower())
            no_videos_found = 'no videos found' in full_output.lower()
            drm_protected = 'drm' in full_output.lower() and 'protected' in full_output.lower()

            # Determine if download actually succeeded
            success = process.returncode == 0 and not token_required and not no_videos_found

            if success:
                self.downloads[download_id]['status'] = 'completed'

                # Create summary message
                total = self.downloads[download_id].get('total_episodes', 0)
                completed = self.downloads[download_id].get('completed_episodes', 0)
                skipped = self.downloads[download_id].get('skipped_episodes', 0)

                if total > 0:
                    self.downloads[download_id]['message'] = f'Season download completed: {completed} downloaded, {skipped} skipped (already existed)'
                else:
                    self.downloads[download_id]['message'] = 'Season download completed'

                self.downloads[download_id]['progress'] = 100
                self.downloads[download_id]['finished_at'] = datetime.now().isoformat()
            else:
                self.downloads[download_id]['status'] = 'failed'

                # Provide specific error messages
                if token_required:
                    self.downloads[download_id]['message'] = 'Token required or expired'
                    self.downloads[download_id]['error'] = 'This content requires a valid TV4 Play token. Please check that you have entered a token and that it has not expired. Click the "?" button next to the Token field for instructions.'
                elif no_videos_found:
                    self.downloads[download_id]['message'] = 'No videos found'
                    self.downloads[download_id]['error'] = 'No videos were found at this URL. Please check the URL or try logging in to TV4 Play and refreshing your token.'
                elif drm_protected:
                    self.downloads[download_id]['message'] = 'DRM protected content'
                    self.downloads[download_id]['error'] = 'This content is DRM protected and cannot be downloaded.'
                else:
                    self.downloads[download_id]['message'] = 'Season download failed'
                    self.downloads[download_id]['error'] = stderr or stdout or 'Unknown error'

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

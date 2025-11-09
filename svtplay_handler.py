import subprocess
import json
import os
import sys
import threading
import queue
import re
from datetime import datetime
from config import Config
import requests
from bs4 import BeautifulSoup

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

def get_env_with_local_bin():
    """Get environment variables with bin/ folder and FFmpeg added to PATH"""
    env = os.environ.copy()

    # Add local bin folder to PATH (for local ffmpeg)
    bin_path = os.path.join(Config.BASE_DIR, 'bin')
    if os.path.exists(bin_path):
        env['PATH'] = bin_path + os.pathsep + env.get('PATH', '')

    # Add FFmpeg from imageio-ffmpeg or Config.FFMPEG_PATH to PATH
    if Config.FFMPEG_PATH:
        ffmpeg_dir = os.path.dirname(Config.FFMPEG_PATH)
        if ffmpeg_dir and os.path.exists(ffmpeg_dir):
            env['PATH'] = ffmpeg_dir + os.pathsep + env.get('PATH', '')

    return env

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

    def list_episodes(self, url, token=None):
        """List all episodes from a series URL

        Args:
            url: The series/category URL to list episodes from
            token: Optional TV4 Play token for authentication
        """
        try:
            # Use --get-only-episode-url with --all-episodes to get episode URLs
            cmd = SVTPLAY_DL_CMD + ['--get-only-episode-url', '--all-episodes']

            # Add token if provided (for TV4 Play)
            if token:
                cmd.extend(['--token', token])

            cmd.append(url)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=get_env_with_local_bin())

            episodes = []
            # Parse both stdout and stderr as svtplay-dl may output to either
            output = (result.stdout or '') + '\n' + (result.stderr or '')

            # Debug logging
            print(f"DEBUG list_episodes: Return code: {result.returncode}")
            print(f"DEBUG list_episodes: Output length: {len(output)}")

            for line in output.split('\n'):
                line = line.strip()
                # Look for URLs (both http and https) - extract just the URL part
                if 'http://' in line or 'https://' in line:
                    # Extract URL from lines like "INFO: Url: http://..."
                    if 'Url:' in line:
                        url_part = line.split('Url:', 1)[1].strip()
                        if url_part and url_part not in episodes:
                            episodes.append(url_part)
                    # Also handle plain URLs
                    elif line.startswith('http://') or line.startswith('https://'):
                        if line not in episodes:
                            episodes.append(line)

            print(f"DEBUG list_episodes: Found {len(episodes)} episodes")

            return {
                'success': True,
                'episodes': episodes,
                'count': len(episodes)
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Request timed out while getting episodes'}
        except Exception as e:
            print(f"DEBUG list_episodes: Exception: {e}")
            return {'success': False, 'error': str(e)}

    def scrape_videos_with_metadata(self, url, max_videos=50, token=None):
        """
        Scrape a URL and return all videos with metadata.
        Strategy:
        1. Get all video URLs from svtplay-dl (authoritative source)
        2. Fetch thumbnails from individual video pages in parallel (og:image)

        Args:
            url: The category/series URL to scrape
            max_videos: Maximum number of videos to return
            token: Optional TV4 Play token for authentication
        """
        try:
            # First, get all episode URLs from svtplay-dl
            episodes_result = self.list_episodes(url, token)

            if not episodes_result['success']:
                return episodes_result

            episode_urls = episodes_result['episodes']

            if not episode_urls or len(episode_urls) == 0:
                return {'success': False, 'error': 'No videos found at this URL'}

            # Limit the number of videos to avoid overwhelming the UI
            limited_urls = episode_urls[:max_videos]

            # Fetch thumbnails in parallel for ALL videos
            print(f"Fetching thumbnails for {len(limited_urls)} videos in parallel...")
            thumbnail_map = self._fetch_thumbnails_parallel(limited_urls)
            print(f"Successfully fetched {len(thumbnail_map)} thumbnails")

            # Build video list matching URLs with thumbnails
            videos = []
            for idx, ep_url in enumerate(limited_urls):
                try:
                    title = self._extract_title_from_url(ep_url)
                    thumbnail = thumbnail_map.get(ep_url)

                    videos.append({
                        'url': ep_url,
                        'title': title,
                        'thumbnail': thumbnail,
                        'duration': None,  # Not available without --json-info
                        'description': '',
                        'season': None,
                        'episode': None  # Don't show episode numbers for movies
                    })
                except Exception as e:
                    print(f"Error parsing {ep_url}: {e}")
                    videos.append({
                        'url': ep_url,
                        'title': f'Video {idx + 1}',
                        'thumbnail': None,
                        'duration': None,
                        'description': '',
                        'season': None,
                        'episode': None  # Don't show episode numbers for movies
                    })

            print(f"DEBUG scrape_videos_with_metadata: Returning {len(videos)} videos")

            # Sort videos alphabetically by title (Swedish locale-aware)
            # Swedish alphabet: A-Z, Å, Ä, Ö (Å, Ä, Ö come after Z)
            def swedish_sort_key(title):
                """Create a sort key that handles Swedish characters correctly"""
                # Normalize to lowercase for case-insensitive sorting
                s = title.lower()
                # Replace Swedish characters with sortable equivalents that come after 'z'
                s = s.replace('å', 'z{')  # After z
                s = s.replace('ä', 'z|')  # After z and å
                s = s.replace('ö', 'z}')  # After z, å, and ä
                return s

            videos.sort(key=lambda x: swedish_sort_key(x['title']))

            return {
                'success': True,
                'videos': videos,
                'count': len(videos),
                'total_available': len(episode_urls),
                'limited': len(episode_urls) > max_videos
            }

        except Exception as e:
            print(f"DEBUG scrape_videos_with_metadata: Exception: {e}")
            return {'success': False, 'error': str(e)}

    def _extract_title_from_url(self, url):
        """Extract a human-readable title from a SVT Play URL"""
        try:
            # URL format: http://www.svtplay.se/video/ID/title-slug
            parts = url.rstrip('/').split('/')
            if len(parts) >= 5:
                # Get the slug (last part) and clean it up
                slug = parts[-1]
                # Replace hyphens with spaces and capitalize words
                title = slug.replace('-', ' ').title()
                return title
            return "Unknown Video"
        except:
            return "Unknown Video"

    def _extract_video_id(self, url):
        """Extract video ID from SVT Play URL"""
        try:
            # URL format: http://www.svtplay.se/video/ID/title-slug
            parts = url.rstrip('/').split('/')
            if len(parts) >= 5:
                return parts[-2]  # The ID is second to last
            return None
        except:
            return None

    def _fetch_thumbnails_parallel(self, video_urls, max_workers=10):
        """
        Fetch thumbnails for multiple videos in parallel using threading.
        Returns a dict mapping video_url -> thumbnail_url
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        thumbnail_map = {}

        def fetch_single(url):
            try:
                thumbnail = self._fetch_thumbnail_from_url(url)
                return (url, thumbnail)
            except Exception as e:
                print(f"Error fetching thumbnail for {url}: {e}")
                return (url, None)

        # Fetch thumbnails in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_single, url): url for url in video_urls}

            for future in as_completed(futures):
                url, thumbnail = future.result()
                if thumbnail:
                    thumbnail_map[url] = thumbnail

        return thumbnail_map

    def _fetch_thumbnails_from_category_page(self, category_url):
        """
        Fetch all thumbnails from a category page in one request.
        Returns a dict mapping video_id -> thumbnail_url
        """
        try:
            # Fetch the category page
            response = requests.get(category_url, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch category page: {response.status_code}")
                return {}

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            thumbnail_map = {}

            # Find all article elements (each contains a video card)
            articles = soup.find_all('article')
            print(f"Found {len(articles)} article elements")

            for article in articles:
                try:
                    # Find the video link
                    link = article.find('a', href=re.compile(r'/video/'))
                    if not link:
                        continue

                    href = link.get('href', '')
                    # Extract video ID from href like "/video/KNwvrEX/nar-lammen-tystnar"
                    match = re.search(r'/video/([^/]+)/', href)
                    if not match:
                        continue

                    video_id = match.group(1)

                    # Look for div with background-image style
                    # SVT uses inline styles or CSS classes for thumbnails
                    div_with_bg = article.find('div', class_=re.compile(r'c26183281'))
                    if div_with_bg and div_with_bg.get('style'):
                        style = div_with_bg.get('style', '')
                        # Extract URL from background-image: url(...)
                        bg_match = re.search(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
                        if bg_match:
                            thumbnail_url = bg_match.group(1)
                            thumbnail_map[video_id] = thumbnail_url
                            continue

                    # Alternative: look for img tags
                    img = article.find('img')
                    if img:
                        src = img.get('src') or img.get('data-src')
                        if src and ('svtstatic' in src or 'image' in src):
                            thumbnail_map[video_id] = src

                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue

            return thumbnail_map

        except Exception as e:
            print(f"Error fetching thumbnails from category page: {e}")
            return {}

    def _fetch_thumbnail_from_url(self, video_url):
        """Fetch thumbnail from a full SVT Play video URL"""
        try:
            # Fetch the page with a timeout
            response = requests.get(video_url, timeout=5)
            if response.status_code != 200:
                return None

            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to find og:image meta tag (Open Graph image - used for social sharing)
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return og_image.get('content')

            # Try to find Twitter card image
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                return twitter_image.get('content')

            # Try to find any img tag with relevant class or data attributes
            # SVT Play often uses specific patterns
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src', '')
                # Look for image URLs that seem to be thumbnails/posters
                if 'image' in src or 'thumb' in src or 'svtstatic' in src:
                    if src.startswith('http'):
                        return src

            return None

        except Exception as e:
            print(f"Error fetching thumbnail from {video_url}: {e}")
            return None

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

    def _get_service_name(self, url):
        """Detect streaming service from URL"""
        if 'svtplay.se' in url.lower():
            return 'SVT Play'
        elif 'tv4play.se' in url.lower() or 'tv4.se' in url.lower():
            return 'TV4 Play'
        else:
            return 'this service'

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

            # Add output directory and custom filename template (just title, no hash or metadata)
            # Use -o for directory and --filename for template
            cmd.extend(['-o', download_dir])
            cmd.extend(['--filename', '{title}'])

            # Add URL
            cmd.append(url)

            # Debug: Print the command being run
            print("=" * 80)
            print("DEBUG: Running svtplay-dl command (single download):")
            print(" ".join(cmd))
            print("=" * 80)

            # Run download with local ffmpeg in PATH
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=get_env_with_local_bin()  # Add bin/ to PATH for local ffmpeg
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
                # Post-process: merge audio and video if separate files exist
                self._merge_audio_video_if_needed(download_dir)

                self.downloads[download_id]['status'] = 'completed'
                self.downloads[download_id]['message'] = 'Download completed'
                self.downloads[download_id]['progress'] = 100
                self.downloads[download_id]['finished_at'] = datetime.now().isoformat()
            else:
                self.downloads[download_id]['status'] = 'failed'

                # Detect service name for appropriate error messages
                service_name = self._get_service_name(url)

                # Provide specific error messages
                if token_required:
                    self.downloads[download_id]['message'] = 'Token required or expired'
                    if service_name == 'TV4 Play':
                        self.downloads[download_id]['error'] = 'This content requires a valid TV4 Play token. Please check that you have entered a token and that it has not expired. Click the "?" button next to the Token field for instructions.'
                    else:
                        self.downloads[download_id]['error'] = f'This content requires authentication. If this is premium content from {service_name}, you may need to provide a token.'
                elif no_videos_found:
                    self.downloads[download_id]['message'] = 'No videos found'
                    if service_name == 'TV4 Play':
                        self.downloads[download_id]['error'] = 'No videos were found at this URL. Please check the URL or try logging in to TV4 Play and refreshing your token.'
                    else:
                        self.downloads[download_id]['error'] = f'No videos were found at this URL. The video may have been removed, may be geo-blocked, or the URL may be incorrect.'
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

            # Add output directory and custom filename template (just title, no hash or metadata)
            # Use -o for directory and --filename for template
            cmd.extend(['-o', download_dir])
            cmd.extend(['--filename', '{title}'])

            # Add URL
            cmd.append(url)

            # Debug: Print the command being run
            print("=" * 80)
            print("DEBUG: Running svtplay-dl command (season download):")
            print(" ".join(cmd))
            print("=" * 80)

            # Run download with local ffmpeg in PATH
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered for real-time reading
                env=get_env_with_local_bin()  # Add bin/ to PATH for local ffmpeg
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
                # Post-process: merge audio and video if separate files exist
                self._merge_audio_video_if_needed(download_dir)

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

                # Detect service name for appropriate error messages
                service_name = self._get_service_name(url)

                # Provide specific error messages
                if token_required:
                    self.downloads[download_id]['message'] = 'Token required or expired'
                    if service_name == 'TV4 Play':
                        self.downloads[download_id]['error'] = 'This content requires a valid TV4 Play token. Please check that you have entered a token and that it has not expired. Click the "?" button next to the Token field for instructions.'
                    else:
                        self.downloads[download_id]['error'] = f'This content requires authentication. If this is premium content from {service_name}, you may need to provide a token.'
                elif no_videos_found:
                    self.downloads[download_id]['message'] = 'No videos found'
                    if service_name == 'TV4 Play':
                        self.downloads[download_id]['error'] = 'No videos were found at this URL. Please check the URL or try logging in to TV4 Play and refreshing your token.'
                    else:
                        self.downloads[download_id]['error'] = f'No videos were found at this URL. The video may have been removed, may be geo-blocked, or the URL may be incorrect.'
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

    def _merge_audio_video_if_needed(self, download_dir):
        """Merge separate audio and video files into one .mkv file using FFmpeg
        Handles both .ts + .audio.ts and .mp4 + .m4a file pairs"""
        try:
            # Pattern 1: Find .ts files (not .audio.ts)
            video_files = []
            for filename in os.listdir(download_dir):
                if filename.endswith('.ts') and not filename.endswith('.audio.ts'):
                    video_files.append((filename, '.ts', '.audio.ts'))
                elif filename.endswith('.mp4'):
                    # Check if there's a corresponding .m4a file
                    base_name = filename[:-4]  # Remove .mp4
                    m4a_file = base_name + '.m4a'
                    if os.path.exists(os.path.join(download_dir, m4a_file)):
                        video_files.append((filename, '.mp4', '.m4a'))

            # For each video file, merge with corresponding audio file
            for video_file, video_ext, audio_ext in video_files:
                video_path = os.path.join(download_dir, video_file)
                base_name = video_file[:-len(video_ext)]  # Remove video extension
                audio_file = base_name + audio_ext
                audio_path = os.path.join(download_dir, audio_file)

                # If both video and audio files exist, merge them
                if os.path.exists(audio_path):
                    output_file = base_name + '.mkv'
                    output_path = os.path.join(download_dir, output_file)

                    print(f"Merging {video_file} + {audio_file} -> {output_file}")

                    # Use FFmpeg to merge
                    if Config.FFMPEG_PATH:
                        cmd = [
                            Config.FFMPEG_PATH,
                            '-i', video_path,
                            '-i', audio_path,
                            '-map', '0:v',  # Explicitly map video from first input
                            '-map', '1:a',  # Explicitly map audio from second input
                            '-c', 'copy',  # Copy streams without re-encoding
                            '-y',  # Overwrite output file
                            output_path
                        ]

                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=300  # 5 minute timeout
                        )

                        if result.returncode == 0:
                            # Merge successful, delete original files
                            print(f"Merge successful, deleting {video_file} and {audio_file}")
                            os.remove(video_path)
                            os.remove(audio_path)
                        else:
                            print(f"FFmpeg merge failed: {result.stderr}")
                    else:
                        print("FFmpeg not available, skipping merge")

        except Exception as e:
            print(f"Error during merge: {e}")

import os

class Config:
    """Application configuration"""

    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Download directory
    DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')

    # FFmpeg path (check local bin folder first)
    FFMPEG_PATH = None

    # Server configuration
    HOST = '0.0.0.0'  # Listen on all interfaces to be accessible from network
    PORT = 5000
    DEBUG = False

    # Maximum concurrent downloads
    MAX_CONCURRENT_DOWNLOADS = 3

    # Default svtplay-dl options
    DEFAULT_QUALITY = 'best'
    DEFAULT_SUBTITLE = True

    @staticmethod
    def init_app():
        """Initialize application directories and find ffmpeg"""
        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

        # Check for local ffmpeg first (in bin folder)
        local_ffmpeg = os.path.join(Config.BASE_DIR, 'bin', 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
        if os.path.exists(local_ffmpeg):
            Config.FFMPEG_PATH = local_ffmpeg
            print(f"Using local ffmpeg: {local_ffmpeg}")
        else:
            # Check if ffmpeg is in PATH
            import subprocess
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                Config.FFMPEG_PATH = 'ffmpeg'  # Use system ffmpeg
                print("Using system ffmpeg from PATH")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("WARNING: ffmpeg not found. Ensure it's installed or in bin/ folder.")
                Config.FFMPEG_PATH = 'ffmpeg'  # Fallback, will fail if not available

import os

class Config:
    """Application configuration"""

    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Download directory
    DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')

    # FFmpeg path (will be set during init)
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

        # Try to use imageio-ffmpeg (installed via pip)
        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            Config.FFMPEG_PATH = get_ffmpeg_exe()
            print(f"[OK] Using imageio-ffmpeg: {Config.FFMPEG_PATH}")
            return
        except ImportError:
            print("INFO: imageio-ffmpeg not installed")
        except Exception as e:
            print(f"INFO: Could not load imageio-ffmpeg: {e}")

        # Fallback: Check for local ffmpeg in bin folder
        local_ffmpeg = os.path.join(Config.BASE_DIR, 'bin', 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
        if os.path.exists(local_ffmpeg):
            Config.FFMPEG_PATH = local_ffmpeg
            print(f"[OK] Using local ffmpeg: {local_ffmpeg}")
            return

        # Fallback: Check if ffmpeg is in system PATH
        import subprocess
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            Config.FFMPEG_PATH = 'ffmpeg'
            print("[OK] Using system ffmpeg from PATH")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # No ffmpeg found
        print("[WARNING] ffmpeg not found!")
        print("  Install with: pip install imageio-ffmpeg")
        print("  Or download manually to bin/ folder")
        Config.FFMPEG_PATH = 'ffmpeg'  # Fallback, may not work

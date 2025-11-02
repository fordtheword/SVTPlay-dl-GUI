import os

class Config:
    """Application configuration"""

    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Download directory
    DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')

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
        """Initialize application directories"""
        os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

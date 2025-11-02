from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from config import Config
from svtplay_handler import SVTPlayDownloader

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize configuration
Config.init_app()

# Initialize downloader
downloader = SVTPlayDownloader()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    """Get information about a video URL"""
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400

    result = downloader.get_info(url)
    return jsonify(result)

@app.route('/api/episodes', methods=['POST'])
def list_episodes():
    """List all episodes from a series URL"""
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400

    result = downloader.list_episodes(url)
    return jsonify(result)

@app.route('/api/download', methods=['POST'])
def start_download():
    """Start downloading a single video"""
    data = request.get_json()
    url = data.get('url')
    options = data.get('options', {})

    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400

    result = downloader.start_download(url, options)
    return jsonify(result)

@app.route('/api/download/season', methods=['POST'])
def download_season():
    """Download entire season"""
    data = request.get_json()
    url = data.get('url')
    options = data.get('options', {})

    if not url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400

    result = downloader.download_season(url, options)
    return jsonify(result)

@app.route('/api/downloads', methods=['GET'])
def get_downloads():
    """Get all downloads"""
    result = downloader.get_all_downloads()
    return jsonify(result)

@app.route('/api/downloads/<download_id>', methods=['GET'])
def get_download_status(download_id):
    """Get status of a specific download"""
    result = downloader.get_status(download_id)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 404

@app.route('/api/downloads/files', methods=['GET'])
def list_files():
    """List downloaded files"""
    try:
        files = []
        if os.path.exists(Config.DOWNLOAD_DIR):
            for filename in os.listdir(Config.DOWNLOAD_DIR):
                filepath = os.path.join(Config.DOWNLOAD_DIR, filename)
                if os.path.isfile(filepath):
                    files.append({
                        'name': filename,
                        'size': os.path.getsize(filepath),
                        'modified': os.path.getmtime(filepath)
                    })
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/downloads/<path:filename>')
def download_file(filename):
    """Serve downloaded files"""
    return send_from_directory(Config.DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    print("=" * 60)
    print("SVTPlay-dl Web GUI Server")
    print("=" * 60)
    print(f"Starting server on http://{Config.HOST}:{Config.PORT}")
    print(f"Download directory: {Config.DOWNLOAD_DIR}")
    print("=" * 60)
    print("\nAccess the GUI from any computer on your network using:")
    print(f"http://[YOUR_SERVER_IP]:{Config.PORT}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)

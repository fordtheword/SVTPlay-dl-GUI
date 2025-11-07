from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from config import Config
from svtplay_handler import SVTPlayDownloader
from profile_manager import ProfileManager

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize configuration
Config.init_app()

# Initialize downloader and profile manager
downloader = SVTPlayDownloader()
profile_manager = ProfileManager()

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

# Profile management endpoints

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get all saved profiles"""
    result = profile_manager.get_all_profiles()
    return jsonify(result)

@app.route('/api/profiles/<profile_id>', methods=['GET'])
def get_profile(profile_id):
    """Get a specific profile"""
    result = profile_manager.get_profile(profile_id)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 404

@app.route('/api/profiles', methods=['POST'])
def save_profile():
    """Save or update a profile"""
    data = request.get_json()

    name = data.get('name')
    url = data.get('url')
    download_dir = data.get('download_dir')

    if not all([name, url, download_dir]):
        return jsonify({'success': False, 'error': 'Name, URL, and download directory are required'}), 400

    quality = data.get('quality', Config.DEFAULT_QUALITY)
    subtitle = data.get('subtitle', Config.DEFAULT_SUBTITLE)
    download_type = data.get('download_type', 'single')
    token = data.get('token')  # Optional

    result = profile_manager.save_profile(name, url, download_dir, quality, subtitle, download_type, token)
    return jsonify(result)

@app.route('/api/profiles/<profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """Delete a profile"""
    result = profile_manager.delete_profile(profile_id)
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 404

@app.route('/api/profiles/search', methods=['GET'])
def search_profiles():
    """Search profiles by name"""
    query = request.args.get('q', '')
    result = profile_manager.search_profiles(query)
    return jsonify(result)

# System management endpoints

@app.route('/api/system/upgrade', methods=['POST'])
def upgrade_system():
    """Upgrade the application (git pull + pip install)"""
    import subprocess
    try:
        # Run git pull
        git_result = subprocess.run(
            ['git', 'pull'],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Config.BASE_DIR
        )

        if git_result.returncode != 0:
            return jsonify({
                'success': False,
                'error': f'Git pull failed: {git_result.stderr}'
            }), 500

        git_output = git_result.stdout

        # Run pip install --upgrade
        pip_result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--upgrade'],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=Config.BASE_DIR
        )

        if pip_result.returncode != 0:
            return jsonify({
                'success': False,
                'error': f'Pip upgrade failed: {pip_result.stderr}',
                'git_output': git_output
            }), 500

        return jsonify({
            'success': True,
            'message': 'Upgrade completed successfully',
            'git_output': git_output,
            'pip_output': pip_result.stdout,
            'restart_required': 'Already up to date' not in git_output
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Upgrade timed out'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """Get system information"""
    import subprocess
    try:
        # Get Python version
        python_version = sys.version.split()[0]

        # Get svtplay-dl version
        svtplay_result = subprocess.run(
            [sys.executable, '-m', 'svtplay_dl', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        svtplay_version = svtplay_result.stdout.strip() if svtplay_result.returncode == 0 else 'Unknown'

        # Get git branch
        git_branch_result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Config.BASE_DIR
        )
        git_branch = git_branch_result.stdout.strip() if git_branch_result.returncode == 0 else 'Unknown'

        # Get latest commit
        git_log_result = subprocess.run(
            ['git', 'log', '-1', '--oneline'],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Config.BASE_DIR
        )
        latest_commit = git_log_result.stdout.strip() if git_log_result.returncode == 0 else 'Unknown'

        return jsonify({
            'success': True,
            'info': {
                'python_version': python_version,
                'svtplay_dl_version': svtplay_version,
                'git_branch': git_branch,
                'latest_commit': latest_commit,
                'download_dir': Config.DOWNLOAD_DIR
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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

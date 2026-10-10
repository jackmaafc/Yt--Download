from flask import Flask, render_template, request, jsonify
import os
import json
from pathlib import Path
from downloader import manager

app = Flask(__name__)

@app.before_request
def block_external_requests():
    # Only allow localhost/127.0.0.1 to prevent DNS rebinding and cross-origin attacks
    host = request.headers.get('Host', '').split(':')[0]
    if host not in ('127.0.0.1', 'localhost'):
        return jsonify({'error': 'Forbidden: Invalid Host'}), 403
        
    if request.method in ('POST', 'PUT', 'DELETE'):
        # Prevent CSRF by checking Origin or Referer
        origin = request.headers.get('Origin')
        referer = request.headers.get('Referer')
        
        # If neither is present on a state-changing request, we reject it to be safe
        if not origin and not referer:
            return jsonify({'error': 'Forbidden: Missing Origin/Referer'}), 403
            
        allowed = [f"http://127.0.0.1:{request.environ.get('SERVER_PORT')}", f"http://localhost:{request.environ.get('SERVER_PORT')}"]
        
        if origin and origin not in allowed:
            return jsonify({'error': 'Forbidden: Invalid Origin'}), 403
            
        if referer and not any(referer.startswith(a) for a in allowed):
            return jsonify({'error': 'Forbidden: Invalid Referer'}), 403

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

def load_settings():
    default_settings = {
        'use_defaults': False,
        'format_type': 'video',
        'quality': 'best',
        'save_path': str(Path.home() / 'Downloads')
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                default_settings.update(settings)
        except Exception:
            pass
    return default_settings

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except Exception:
        pass

@app.route('/')
def index():
    settings = load_settings()
    return render_template('index.html', settings=settings)

@app.route('/api/download', methods=['POST'])
def add_download():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    urls = data.get('urls', [])
    
    if not urls:
        return jsonify({'error': 'No URLs provided'}), 400
        
    settings = load_settings()
    
    # If use_defaults is enabled, use saved settings, else use request data
    if settings.get('use_defaults'):
        format_type = settings.get('format_type', 'video')
        quality = settings.get('quality', 'best')
        save_path = settings.get('save_path', str(Path.home() / 'Downloads'))
    else:
        format_type = data.get('format_type', 'video')
        quality = data.get('quality', 'best')
        save_path = data.get('save_path', str(Path.home() / 'Downloads'))

    # Validate save_path is within user's home directory and not a hidden path
    home_dir = os.path.realpath(str(Path.home()))
    try:
        if not save_path:
            save_path = os.path.join(home_dir, 'Downloads')
        resolved_path = os.path.realpath(save_path)
        
        # Prevent traversal outside home and prevent writing to hidden folders
        if not resolved_path.startswith(home_dir) or '/.' in resolved_path.replace(home_dir, ''):
            save_path = os.path.join(home_dir, 'Downloads')
        elif not os.path.exists(resolved_path):
            save_path = os.path.join(home_dir, 'Downloads')
        else:
            save_path = resolved_path
    except Exception:
        save_path = os.path.join(home_dir, 'Downloads')

    import urllib.parse
    valid_urls = []
    for u in urls:
        try:
            parsed = urllib.parse.urlparse(u)
            if parsed.scheme in ('http', 'https'):
                netloc = parsed.netloc.lower()
                if netloc == 'youtube.com' or netloc.endswith('.youtube.com') or netloc == 'youtu.be':
                    valid_urls.append(u)
        except Exception:
            pass
            
    if not valid_urls:
        return jsonify({'error': 'No valid YouTube URLs provided'}), 400

    job_ids = manager.add_job(valid_urls, format_type, quality, save_path)
    return jsonify({'job_ids': job_ids, 'message': 'Jobs added to queue'})

@app.route('/api/queue')
def get_queue():
    jobs = manager.get_all_jobs()
    # Sort by added_at descending
    jobs.sort(key=lambda x: x['added_at'], reverse=True)
    return jsonify(jobs)

@app.route('/api/queue/<job_id>', methods=['DELETE'])
def remove_job(job_id):
    manager.remove_job(job_id)
    return jsonify({'success': True})

@app.route('/api/queue/clear', methods=['POST'])
def clear_completed():
    manager.clear_completed()
    return jsonify({'success': True})

@app.route('/api/settings', methods=['GET', 'POST'])
def manage_settings():
    if request.method == 'POST':
        data = request.json
        current = load_settings()
        current.update(data)
        save_settings(current)
        return jsonify({'success': True, 'settings': current})
    else:
        return jsonify(load_settings())

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    # Flask doesn't have a clean built-in shutdown in newer versions from a request,
    # but we can terminate the process.
    import os
    import signal
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({'success': True})

if __name__ == '__main__':
    # Select available port safely
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    
    print(f"Starting server on http://127.0.0.1:{port}")
    
    import webbrowser
    import threading
    threading.Timer(1.25, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    
    app.run(host='127.0.0.1', port=port, debug=False)

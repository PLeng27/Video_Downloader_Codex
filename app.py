from flask import Flask, jsonify, render_template, request

from services.download_manager import DownloadManager
from services.history_store import HistoryStore
from services.validation import validate_video_url

app = Flask(__name__)

download_manager = DownloadManager()
history_store = HistoryStore()


@app.route('/')
def index():
    return render_template('index.html')


@app.post('/api/metadata')
def metadata():
    payload = request.get_json(silent=True) or {}
    url = (payload.get('url') or '').strip()

    is_valid, reason = validate_video_url(url)
    if not is_valid:
        return jsonify({'error': reason}), 400

    try:
        metadata = download_manager.fetch_metadata(url)
        return jsonify(metadata)
    except Exception as exc:  # noqa: BLE001
        return jsonify({'error': str(exc)}), 400


@app.post('/api/download')
def start_download():
    payload = request.get_json(silent=True) or {}
    url = (payload.get('url') or '').strip()
    format_id = payload.get('format_id')
    audio_only = bool(payload.get('audio_only'))
    save_dir = payload.get('save_dir')

    is_valid, reason = validate_video_url(url)
    if not is_valid:
        return jsonify({'error': reason}), 400

    try:
        task_id = download_manager.start_download(
            url=url,
            format_id=format_id,
            audio_only=audio_only,
            save_dir=save_dir,
            history_store=history_store,
        )
        return jsonify({'task_id': task_id})
    except Exception as exc:  # noqa: BLE001
        return jsonify({'error': str(exc)}), 400


@app.get('/api/download/<task_id>/status')
def status(task_id: str):
    status_data = download_manager.get_status(task_id)
    if not status_data:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(status_data)


@app.get('/api/history')
def history():
    return jsonify({'items': history_store.list_items()})


if __name__ == '__main__':
    app.run(debug=True)

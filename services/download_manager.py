import threading
import uuid
from pathlib import Path
from typing import Any

import yt_dlp

from services.history_store import HistoryStore


class DownloadManager:
    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def fetch_metadata(self, url: str) -> dict[str, Any]:
        options = {
            'quiet': True,
            'noplaylist': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for fmt in info.get('formats', []):
            if fmt.get('vcodec') == 'none' and fmt.get('acodec') == 'none':
                continue
            ext = fmt.get('ext', '')
            height = fmt.get('height')
            label = f"{ext.upper()}"
            if height:
                label += f" - {height}p"
            filesize = fmt.get('filesize') or fmt.get('filesize_approx')
            if filesize:
                label += f" ({round(filesize / 1024 / 1024, 1)} MB)"
            formats.append({'format_id': fmt['format_id'], 'label': label})

        unique_formats = {f['format_id']: f for f in formats}

        return {
            'title': info.get('title'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration'),
            'formats': list(unique_formats.values()),
        }

    def start_download(
        self,
        url: str,
        format_id: str | None,
        audio_only: bool,
        save_dir: str | None,
        history_store: HistoryStore,
    ) -> str:
        task_id = str(uuid.uuid4())
        target_dir = self._resolve_target_directory(save_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        with self._lock:
            self._tasks[task_id] = {
                'status': 'queued',
                'progress': 0,
                'message': 'Queued',
                'file_path': None,
            }

        thread = threading.Thread(
            target=self._download_worker,
            args=(task_id, url, format_id, audio_only, target_dir, history_store),
            daemon=True,
        )
        thread.start()
        return task_id

    def _resolve_target_directory(self, save_dir: str | None) -> Path:
        if save_dir:
            return Path(save_dir).expanduser().resolve()

        default_downloads = Path.home() / 'Downloads'
        if default_downloads.exists():
            return default_downloads
        return Path.home()

    def _update_task(self, task_id: str, **changes: Any) -> None:
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].update(changes)

    def _download_worker(
        self,
        task_id: str,
        url: str,
        format_id: str | None,
        audio_only: bool,
        target_dir: Path,
        history_store: HistoryStore,
    ) -> None:
        output_template = str(target_dir / '%(title)s.%(ext)s')

        def progress_hook(event: dict[str, Any]) -> None:
            if event['status'] == 'downloading':
                downloaded = event.get('downloaded_bytes', 0)
                total = event.get('total_bytes') or event.get('total_bytes_estimate') or 1
                progress = int((downloaded / total) * 100)
                self._update_task(
                    task_id,
                    status='downloading',
                    progress=progress,
                    message=event.get('_percent_str', 'Downloading').strip(),
                )
            elif event['status'] == 'finished':
                self._update_task(task_id, progress=100, message='Processing file...')

        ydl_opts: dict[str, Any] = {
            'outtmpl': output_template,
            'noplaylist': True,
            'progress_hooks': [progress_hook],
        }

        if audio_only:
            ydl_opts.update(
                {
                    'format': 'bestaudio/best',
                    'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }
                    ],
                }
            )
        else:
            ydl_opts['format'] = format_id or 'bestvideo+bestaudio/best'
            ydl_opts['merge_output_format'] = 'mp4'

        self._update_task(task_id, status='starting', message='Starting download...')

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if audio_only:
                file_path = str(Path(file_path).with_suffix('.mp3'))

            history_store.add_item(
                {
                    'title': info.get('title'),
                    'url': url,
                    'file_path': file_path,
                    'audio_only': audio_only,
                }
            )
            self._update_task(
                task_id,
                status='completed',
                progress=100,
                message='Download completed successfully.',
                file_path=file_path,
            )
        except Exception as exc:  # noqa: BLE001
            self._update_task(task_id, status='failed', message=str(exc))

    def get_status(self, task_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._tasks.get(task_id)
            return dict(data) if data else None

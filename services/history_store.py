import json
from datetime import datetime
from pathlib import Path
from typing import Any


class HistoryStore:
    def __init__(self, history_path: Path | None = None) -> None:
        self.history_path = history_path or Path.home() / '.video_downloader_history.json'
        if not self.history_path.exists():
            self.history_path.write_text('[]', encoding='utf-8')

    def _read(self) -> list[dict[str, Any]]:
        try:
            return json.loads(self.history_path.read_text(encoding='utf-8'))
        except Exception:  # noqa: BLE001
            return []

    def _write(self, data: list[dict[str, Any]]) -> None:
        self.history_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def add_item(self, item: dict[str, Any]) -> None:
        items = self._read()
        item['downloaded_at'] = datetime.utcnow().isoformat() + 'Z'
        items.insert(0, item)
        self._write(items[:100])

    def list_items(self) -> list[dict[str, Any]]:
        return self._read()

"""Persists the best win streak across runs of the game."""

import json
from pathlib import Path


class HighScore:
    """Reads and writes a single best-streak number to a JSON file."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.value: int = self._load()

    def _load(self) -> int:
        if not self.file_path.exists():
            return 0
        try:
            data = json.loads(self.file_path.read_text())
            return int(data.get("best_streak", 0))
        except (json.JSONDecodeError, ValueError, OSError):
            return 0

    def update_if_higher(self, streak: int) -> bool:
        """Save streak as the new best if it beats the current one."""
        if streak <= self.value:
            return False
        self.value = streak
        self._save()
        return True

    def _save(self) -> None:
        self.file_path.write_text(json.dumps({"best_streak": self.value}))

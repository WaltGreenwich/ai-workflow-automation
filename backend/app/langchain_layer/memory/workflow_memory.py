"""In-memory conversation history store keyed by session_id."""
from collections import defaultdict
from datetime import datetime


class WorkflowMemory:
    _store: dict = defaultdict(list)

    def add_message(self, session_id: str, role: str, content: str) -> None:
        self._store[session_id].append({
            "role": role, "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        if len(self._store[session_id]) > 50:
            self._store[session_id] = self._store[session_id][-50:]

    def get_history(self, session_id: str) -> list:
        return list(self._store.get(session_id, []))

    def clear_session(self, session_id: str) -> None:
        self._store.pop(session_id, None)

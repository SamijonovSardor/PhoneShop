"""Conversation memory - SQLite orqali suhbat tarixini saqlash.

Har bir foydalanuvchi (chat_id) uchun alohida tarix saqlanadi.
Sliding window yondashuvi: faqat oxirgi N ta xabar saqlanadi.
"""
import sqlite3
import threading
from pathlib import Path
from typing import List, Dict, Optional
from .config import settings, PROJECT_ROOT

DEFAULT_MAX_MESSAGES = 6


class ConversationMemory:
    """Foydalanuvchi suhbat tarixini SQLite'da saqlash."""

    def __init__(
        self,
        db_path: Optional[str] = None,
        max_messages: int = DEFAULT_MAX_MESSAGES,
    ) -> None:
        self.db_path = Path(db_path or PROJECT_ROOT / "data" / "conversations.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_messages = max_messages
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id    INTEGER NOT NULL,
                    role       TEXT    NOT NULL CHECK (role IN ('user', 'assistant')),
                    content    TEXT    NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_id_id
                ON messages (chat_id, id)
            """)
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def add_message(self, chat_id: int, role: str, content: str) -> None:
        """Yangi xabar qo'shish va keraksiz eski xabarlarni o'chirish."""
        if role not in ("user", "assistant"):
            raise ValueError(f"role 'user' yoki 'assistant' bo'lishi kerak: {role}")
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                    (chat_id, role, content),
                )
                conn.execute(
                    """
                    DELETE FROM messages
                    WHERE chat_id = ?
                      AND id NOT IN (
                          SELECT id FROM messages
                          WHERE chat_id = ?
                          ORDER BY id DESC
                          LIMIT ?
                      )
                    """,
                    (chat_id, chat_id, self.max_messages),
                )
                conn.commit()

    def get_history(self, chat_id: int) -> List[Dict[str, str]]:
        """Foydalanuvchining oxirgi N ta xabari (eski -> yangi tartibda)."""
        with self._lock:
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT role, content FROM messages
                    WHERE chat_id = ?
                    ORDER BY id ASC
                    """,
                    (chat_id,),
                ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in rows]

    def clear(self, chat_id: int) -> int:
        """Foydalanuvchi tarixini tozalash. O'chirilgan xabarlar sonini qaytaradi."""
        with self._lock:
            with self._connect() as conn:
                cursor = conn.execute(
                    "DELETE FROM messages WHERE chat_id = ?", (chat_id,)
                )
                deleted = cursor.rowcount
                conn.commit()
        return deleted

    def count(self, chat_id: int) -> int:
        """Foydalanuvchining saqlangan xabarlar soni."""
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT COUNT(*) FROM messages WHERE chat_id = ?", (chat_id,)
                ).fetchone()
        return row[0] if row else 0

    def total_users(self) -> int:
        """Nechta noyob foydalanuvchi suhbat boshlagan."""
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT COUNT(DISTINCT chat_id) FROM messages"
                ).fetchone()
        return row[0] if row else 0


memory = ConversationMemory(max_messages=DEFAULT_MAX_MESSAGES)

"""SQLite persistence layer for TechWise conversations and messages."""

import json
import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = "techwise_chats.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _init_db() -> None:
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                build_json TEXT,
                is_error INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
        """)
    conn.close()


_init_db()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_conversation(title: str, category: str | None = None) -> str:
    conv_id = uuid.uuid4().hex[:12]
    now = _now()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO conversations (id, title, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (conv_id, title.strip() or "New chat", category, now, now),
        )
    conn.close()
    return conv_id


def update_conversation_title(conv_id: str, title: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
            (title.strip(), _now(), conv_id),
        )
    conn.close()


def add_message(
    conv_id: str,
    role: str,
    content: str,
    build: dict | None = None,
    is_error: bool = False,
) -> None:
    now = _now()
    build_json = json.dumps(build, ensure_ascii=False) if build else None
    with _connect() as conn:
        conn.execute(
            """INSERT INTO messages (conversation_id, role, content, build_json, is_error, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (conv_id, role, content, build_json, int(is_error), now),
        )
        conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conv_id))
    conn.close()


def pop_last_two_messages(conv_id: str) -> None:
    """Removes the last failed assistant reply and user prompt on retry."""
    with _connect() as conn:
        conn.execute(
            """DELETE FROM messages WHERE id IN (
                   SELECT id FROM messages WHERE conversation_id = ?
                   ORDER BY id DESC LIMIT 2
               )""",
            (conv_id,),
        )
    conn.close()


def list_conversations(limit: int = 12) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, title, category, updated_at FROM conversations ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_messages(conv_id: str) -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT role, content, build_json, is_error FROM messages WHERE conversation_id = ? ORDER BY id ASC",
            (conv_id,),
        ).fetchall()
    conn.close()
    return [
        {
            "role": r["role"],
            "content": r["content"],
            "build": json.loads(r["build_json"]) if r["build_json"] else None,
            "error": bool(r["is_error"]),
        }
        for r in rows
    ]


def delete_conversation(conv_id: str) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
    conn.close()
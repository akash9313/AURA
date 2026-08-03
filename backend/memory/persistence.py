import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, List, Tuple

logger = logging.getLogger("AURA.Memory.Persistence")


class SQLiteDatabase:
    """
    Manages SQLite database connections, schema initialization, and transactional queries.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(backend_dir, "aura_memory.db")

        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for SQLite connections with WAL mode and foreign key constraints."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise e
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Create database tables if they do not exist."""
        logger.info(f"Initializing SQLite database at '{self.db_path}'")
        with self.get_connection() as conn:
            # 1. Profile Facts Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profile_facts (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'preference',
                    updated_at TEXT NOT NULL
                );
            """)

            # 2. Conversations Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    summary TEXT NOT NULL DEFAULT '',
                    keywords_json TEXT NOT NULL DEFAULT '[]',
                    started_at TEXT NOT NULL,
                    finished_at TEXT
                );
            """)

            # 3. Conversation Messages Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
                );
            """)

            # 4. Knowledge Documents Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    doc_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    doc_type TEXT NOT NULL DEFAULT 'text',
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
            """)

    def execute_query(self, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_statement(self, statement: str, params: Tuple[Any, ...] = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE statement and return affected rowcount."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(statement, params)
            return cursor.rowcount

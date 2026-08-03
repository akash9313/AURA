import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
from memory.models import (
    ConversationMessage,
    ConversationRecord,
    KnowledgeDocument,
    ProfileFact,
)
from memory.persistence import SQLiteDatabase

logger = logging.getLogger("AURA.Memory.Store")


class BaseMemoryRepository(ABC):
    """
    Abstract Repository interface for persistent memory storage.

    Decouples storage mechanism (SQLite, PostgreSQL, VectorDB) from core business logic.
    """

    # --- Profile Memory Repository Methods ---
    @abstractmethod
    def save_profile_fact(self, fact: ProfileFact) -> None:
        pass

    @abstractmethod
    def get_profile_fact(self, key: str) -> Optional[ProfileFact]:
        pass

    @abstractmethod
    def delete_profile_fact(self, key: str) -> bool:
        pass

    @abstractmethod
    def list_profile_facts(self) -> List[ProfileFact]:
        pass

    # --- Conversation Memory Repository Methods ---
    @abstractmethod
    def save_conversation(self, record: ConversationRecord) -> None:
        pass

    @abstractmethod
    def get_conversation(self, conversation_id: str) -> Optional[ConversationRecord]:
        pass

    @abstractmethod
    def search_conversations(self, query: str, limit: int = 10) -> List[ConversationRecord]:
        pass

    @abstractmethod
    def list_conversations(self, limit: int = 10) -> List[ConversationRecord]:
        pass

    # --- Knowledge Memory Repository Methods ---
    @abstractmethod
    def save_knowledge_doc(self, doc: KnowledgeDocument) -> None:
        pass

    @abstractmethod
    def get_knowledge_doc(self, doc_id: str) -> Optional[KnowledgeDocument]:
        pass

    @abstractmethod
    def search_knowledge_docs(self, query: str, limit: int = 10) -> List[KnowledgeDocument]:
        pass


class SQLiteMemoryRepository(BaseMemoryRepository):
    """
    Concrete SQLite implementation of the BaseMemoryRepository.
    """

    def __init__(self, db: SQLiteDatabase = None):
        self.db = db if db is not None else SQLiteDatabase()

    # --- Profile Memory ---
    def save_profile_fact(self, fact: ProfileFact) -> None:
        statement = """
            INSERT INTO profile_facts (key, value, category, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                category = excluded.category,
                updated_at = excluded.updated_at;
        """
        self.db.execute_statement(
            statement,
            (fact.key, fact.value, fact.category, fact.updated_at.isoformat())
        )
        logger.info(f"Saved profile fact: '{fact.key}' -> '{fact.value}' [{fact.category}]")

    def get_profile_fact(self, key: str) -> Optional[ProfileFact]:
        rows = self.db.execute_query(
            "SELECT key, value, category, updated_at FROM profile_facts WHERE key = ?;",
            (key,)
        )
        if not rows:
            return None
        row = rows[0]
        return ProfileFact(
            key=row["key"],
            value=row["value"],
            category=row["category"],
            updated_at=datetime.fromisoformat(row["updated_at"])
        )

    def delete_profile_fact(self, key: str) -> bool:
        affected = self.db.execute_statement(
            "DELETE FROM profile_facts WHERE key = ?;",
            (key,)
        )
        return affected > 0

    def list_profile_facts(self) -> List[ProfileFact]:
        rows = self.db.execute_query(
            "SELECT key, value, category, updated_at FROM profile_facts ORDER BY updated_at DESC;"
        )
        return [
            ProfileFact(
                key=row["key"],
                value=row["value"],
                category=row["category"],
                updated_at=datetime.fromisoformat(row["updated_at"])
            )
            for row in rows
        ]

    # --- Conversation Memory ---
    def save_conversation(self, record: ConversationRecord) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # 1. Upsert conversation header
            cursor.execute("""
                INSERT INTO conversations (conversation_id, title, summary, keywords_json, started_at, finished_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(conversation_id) DO UPDATE SET
                    title = excluded.title,
                    summary = excluded.summary,
                    keywords_json = excluded.keywords_json,
                    finished_at = excluded.finished_at;
            """, (
                record.conversation_id,
                record.title,
                record.summary,
                json.dumps(record.keywords),
                record.started_at.isoformat(),
                record.finished_at.isoformat() if record.finished_at else None
            ))

            # 2. Insert messages
            cursor.execute("DELETE FROM conversation_messages WHERE conversation_id = ?;", (record.conversation_id,))
            for msg in record.messages:
                cursor.execute("""
                    INSERT INTO conversation_messages (conversation_id, role, content, timestamp)
                    VALUES (?, ?, ?, ?);
                """, (
                    record.conversation_id,
                    msg.role,
                    msg.content,
                    msg.timestamp.isoformat()
                ))
        logger.info(f"Saved conversation session: '{record.conversation_id}' with {len(record.messages)} message(s).")

    def get_conversation(self, conversation_id: str) -> Optional[ConversationRecord]:
        header_rows = self.db.execute_query(
            "SELECT conversation_id, title, summary, keywords_json, started_at, finished_at FROM conversations WHERE conversation_id = ?;",
            (conversation_id,)
        )
        if not header_rows:
            return None
        h = header_rows[0]

        msg_rows = self.db.execute_query(
            "SELECT role, content, timestamp FROM conversation_messages WHERE conversation_id = ? ORDER BY id ASC;",
            (conversation_id,)
        )
        messages = [
            ConversationMessage(
                role=row["role"],
                content=row["content"],
                timestamp=datetime.fromisoformat(row["timestamp"])
            )
            for row in msg_rows
        ]

        return ConversationRecord(
            conversation_id=h["conversation_id"],
            title=h["title"],
            summary=h["summary"],
            keywords=json.loads(h["keywords_json"]),
            messages=messages,
            started_at=datetime.fromisoformat(h["started_at"]),
            finished_at=datetime.fromisoformat(h["finished_at"]) if h["finished_at"] else None
        )

    def search_conversations(self, query: str, limit: int = 10) -> List[ConversationRecord]:
        like_pattern = f"%{query}%"
        rows = self.db.execute_query("""
            SELECT DISTINCT c.conversation_id
            FROM conversations c
            LEFT JOIN conversation_messages m ON c.conversation_id = m.conversation_id
            WHERE c.title LIKE ? OR c.summary LIKE ? OR c.keywords_json LIKE ? OR m.content LIKE ?
            ORDER BY c.started_at DESC
            LIMIT ?;
        """, (like_pattern, like_pattern, like_pattern, like_pattern, limit))

        results = []
        for r in rows:
            record = self.get_conversation(r["conversation_id"])
            if record:
                results.append(record)
        return results

    def list_conversations(self, limit: int = 10) -> List[ConversationRecord]:
        rows = self.db.execute_query(
            "SELECT conversation_id FROM conversations ORDER BY started_at DESC LIMIT ?;",
            (limit,)
        )
        results = []
        for r in rows:
            record = self.get_conversation(r["conversation_id"])
            if record:
                results.append(record)
        return results

    # --- Knowledge Memory ---
    def save_knowledge_doc(self, doc: KnowledgeDocument) -> None:
        statement = """
            INSERT INTO knowledge_documents (doc_id, title, content, doc_type, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(doc_id) DO UPDATE SET
                title = excluded.title,
                content = excluded.content,
                doc_type = excluded.doc_type,
                metadata_json = excluded.metadata_json;
        """
        self.db.execute_statement(
            statement,
            (
                doc.doc_id,
                doc.title,
                doc.content,
                doc.doc_type,
                json.dumps(doc.metadata),
                doc.created_at.isoformat()
            )
        )
        logger.info(f"Saved knowledge document: '{doc.title}' ({doc.doc_id})")

    def get_knowledge_doc(self, doc_id: str) -> Optional[KnowledgeDocument]:
        rows = self.db.execute_query(
            "SELECT doc_id, title, content, doc_type, metadata_json, created_at FROM knowledge_documents WHERE doc_id = ?;",
            (doc_id,)
        )
        if not rows:
            return None
        row = rows[0]
        return KnowledgeDocument(
            doc_id=row["doc_id"],
            title=row["title"],
            content=row["content"],
            doc_type=row["doc_type"],
            metadata=json.loads(row["metadata_json"]),
            created_at=datetime.fromisoformat(row["created_at"])
        )

    def search_knowledge_docs(self, query: str, limit: int = 10) -> List[KnowledgeDocument]:
        like_pattern = f"%{query}%"
        rows = self.db.execute_query("""
            SELECT doc_id, title, content, doc_type, metadata_json, created_at
            FROM knowledge_documents
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?;
        """, (like_pattern, like_pattern, limit))

        return [
            KnowledgeDocument(
                doc_id=row["doc_id"],
                title=row["title"],
                content=row["content"],
                doc_type=row["doc_type"],
                metadata=json.loads(row["metadata_json"]),
                created_at=datetime.fromisoformat(row["created_at"])
            )
            for row in rows
        ]

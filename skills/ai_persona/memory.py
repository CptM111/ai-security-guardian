"""
AI Security Guardian — AI Persona Skill
Memory Engine: Long-Term Memory via SQLite + Cosine Similarity

Architecture:
  - Every memory (conversation turn or fed document) is stored as:
      text  |  embedding (JSON-serialised float list)  |  metadata
  - At recall time, the query is embedded and the top-K most similar
    memories are retrieved via cosine similarity computed in Python/NumPy.
  - No external vector database required — fully self-contained.

Version: 1.0.0
"""

import os
import json
import sqlite3
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

import numpy as np

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

class MemoryEntry:
    """A single memory record."""

    def __init__(
        self,
        memory_id: str,
        persona_id: str,
        content: str,
        embedding: List[float],
        memory_type: str = "conversation",   # conversation | knowledge | alignment
        metadata: Optional[Dict] = None,
        created_at: Optional[str] = None,
        importance: float = 1.0,
    ):
        self.memory_id = memory_id
        self.persona_id = persona_id
        self.content = content
        self.embedding = embedding
        self.memory_type = memory_type
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.importance = importance

    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "persona_id": self.persona_id,
            "content": self.content,
            "memory_type": self.memory_type,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "importance": self.importance,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Embedding provider (OpenAI text-embedding-3-small)
# ─────────────────────────────────────────────────────────────────────────────

class EmbeddingProvider:
    """Thin wrapper around OpenAI embeddings with a local cache."""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self._client = None
        self._cache: Dict[str, List[float]] = {}

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def embed(self, text: str) -> List[float]:
        """Return embedding vector for *text*. Uses in-process cache."""
        key = hashlib.md5(text.encode()).hexdigest()
        if key in self._cache:
            return self._cache[key]
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text[:8000],   # guard against token overflow
            )
            vec = response.data[0].embedding
        except Exception as e:
            logger.warning(f"Embedding API error: {e}. Using zero vector.")
            vec = [0.0] * 1536
        self._cache[key] = vec
        return vec

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts in a single API call."""
        uncached = [(i, t) for i, t in enumerate(texts)
                    if hashlib.md5(t.encode()).hexdigest() not in self._cache]
        if uncached:
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=[t[:8000] for _, t in uncached],
                )
                for (i, t), item in zip(uncached, response.data):
                    key = hashlib.md5(t.encode()).hexdigest()
                    self._cache[key] = item.embedding
            except Exception as e:
                logger.warning(f"Batch embedding error: {e}")
        return [self.embed(t) for t in texts]


# ─────────────────────────────────────────────────────────────────────────────
# Memory store (SQLite)
# ─────────────────────────────────────────────────────────────────────────────

class PersonaMemoryStore:
    """
    SQLite-backed persistent memory store for all Personas.

    Schema
    ------
    personas  : id, name, system_prompt, traits (JSON), created_at, updated_at
    memories  : id, persona_id, content, embedding (JSON), memory_type,
                metadata (JSON), created_at, importance
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS personas (
        id          TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        system_prompt TEXT NOT NULL DEFAULT '',
        traits      TEXT NOT NULL DEFAULT '{}',
        created_at  TEXT NOT NULL,
        updated_at  TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS memories (
        id          TEXT PRIMARY KEY,
        persona_id  TEXT NOT NULL,
        content     TEXT NOT NULL,
        embedding   TEXT NOT NULL,
        memory_type TEXT NOT NULL DEFAULT 'conversation',
        metadata    TEXT NOT NULL DEFAULT '{}',
        created_at  TEXT NOT NULL,
        importance  REAL NOT NULL DEFAULT 1.0,
        FOREIGN KEY (persona_id) REFERENCES personas(id)
    );

    CREATE INDEX IF NOT EXISTS idx_memories_persona ON memories(persona_id);
    CREATE INDEX IF NOT EXISTS idx_memories_type    ON memories(persona_id, memory_type);
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.expanduser("~/.asg/personas.db")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript(self.SCHEMA)

    # ── Persona CRUD ──────────────────────────────────────────────────────────

    def create_persona(
        self,
        persona_id: str,
        name: str,
        system_prompt: str = "",
        traits: Optional[Dict] = None,
    ) -> Dict:
        now = datetime.now(timezone.utc).isoformat()
        traits_json = json.dumps(traits or {})
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO personas VALUES (?,?,?,?,?,?)",
                (persona_id, name, system_prompt, traits_json, now, now),
            )
        return self.get_persona(persona_id)

    def get_persona(self, persona_id: str) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM personas WHERE id=?", (persona_id,)
            ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["traits"] = json.loads(d["traits"])
        return d

    def list_personas(self) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, name, created_at, updated_at FROM personas ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def update_persona(self, persona_id: str, **kwargs) -> Optional[Dict]:
        allowed = {"name", "system_prompt", "traits"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return self.get_persona(persona_id)
        now = datetime.now(timezone.utc).isoformat()
        set_clause = ", ".join(f"{k}=?" for k in updates)
        values = list(updates.values())
        if "traits" in updates:
            idx = list(updates.keys()).index("traits")
            values[idx] = json.dumps(values[idx])
        values += [now, persona_id]
        with self._conn() as conn:
            conn.execute(
                f"UPDATE personas SET {set_clause}, updated_at=? WHERE id=?",
                values,
            )
        return self.get_persona(persona_id)

    def delete_persona(self, persona_id: str):
        with self._conn() as conn:
            conn.execute("DELETE FROM memories WHERE persona_id=?", (persona_id,))
            conn.execute("DELETE FROM personas WHERE id=?", (persona_id,))

    # ── Memory CRUD ───────────────────────────────────────────────────────────

    def add_memory(self, entry: MemoryEntry):
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO memories VALUES (?,?,?,?,?,?,?,?)",
                (
                    entry.memory_id,
                    entry.persona_id,
                    entry.content,
                    json.dumps(entry.embedding),
                    entry.memory_type,
                    json.dumps(entry.metadata),
                    entry.created_at,
                    entry.importance,
                ),
            )

    def get_all_memories(
        self,
        persona_id: str,
        memory_type: Optional[str] = None,
    ) -> List[MemoryEntry]:
        with self._conn() as conn:
            if memory_type:
                rows = conn.execute(
                    "SELECT * FROM memories WHERE persona_id=? AND memory_type=? ORDER BY created_at DESC",
                    (persona_id, memory_type),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM memories WHERE persona_id=? ORDER BY created_at DESC",
                    (persona_id,),
                ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def count_memories(self, persona_id: str) -> int:
        with self._conn() as conn:
            return conn.execute(
                "SELECT COUNT(*) FROM memories WHERE persona_id=?", (persona_id,)
            ).fetchone()[0]

    def clear_memories(self, persona_id: str, memory_type: Optional[str] = None):
        with self._conn() as conn:
            if memory_type:
                conn.execute(
                    "DELETE FROM memories WHERE persona_id=? AND memory_type=?",
                    (persona_id, memory_type),
                )
            else:
                conn.execute(
                    "DELETE FROM memories WHERE persona_id=?", (persona_id,)
                )

    def _row_to_entry(self, row: sqlite3.Row) -> MemoryEntry:
        return MemoryEntry(
            memory_id=row["id"],
            persona_id=row["persona_id"],
            content=row["content"],
            embedding=json.loads(row["embedding"]),
            memory_type=row["memory_type"],
            metadata=json.loads(row["metadata"]),
            created_at=row["created_at"],
            importance=row["importance"],
        )

    # ── Semantic search ───────────────────────────────────────────────────────

    def search_memories(
        self,
        persona_id: str,
        query_embedding: List[float],
        top_k: int = 5,
        memory_type: Optional[str] = None,
        min_similarity: float = 0.3,
    ) -> List[Tuple[MemoryEntry, float]]:
        """
        Return the *top_k* most semantically similar memories to *query_embedding*.
        Uses cosine similarity computed in NumPy — no external vector DB needed.
        """
        entries = self.get_all_memories(persona_id, memory_type=memory_type)
        if not entries:
            return []

        q = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            return []
        q = q / q_norm

        scored: List[Tuple[MemoryEntry, float]] = []
        for entry in entries:
            vec = np.array(entry.embedding, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm == 0:
                continue
            sim = float(np.dot(q, vec / norm)) * entry.importance
            if sim >= min_similarity:
                scored.append((entry, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

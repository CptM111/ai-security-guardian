"""
AI Security Guardian — AI Persona Skill
Persona Manager: Create, align, and manage AI Personas

A Persona is a named AI avatar with:
  - A fixed identity defined by a system prompt and personality traits
  - Long-term memory that persists across sessions
  - An alignment pipeline: feed arbitrary text to shape its knowledge base
  - A secure chat interface protected by ASG's security layer

Version: 1.0.0
"""

import uuid
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple

from .memory import PersonaMemoryStore, MemoryEntry, EmbeddingProvider

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Persona Manager
# ─────────────────────────────────────────────────────────────────────────────

class PersonaManager:
    """
    High-level API for creating and managing AI Personas.

    Usage
    -----
    mgr = PersonaManager()

    # Create a persona
    persona = mgr.create("Alice", system_prompt="You are Alice, a senior security researcher...")

    # Feed knowledge to align the persona
    mgr.feed(persona["id"], "Alice specialises in zero-day vulnerability research...")

    # Chat
    reply = mgr.chat(persona["id"], "What is your area of expertise?")
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        llm_model: str = "gpt-4.1-mini",
        embedding_model: str = "text-embedding-3-small",
        memory_top_k: int = 5,
    ):
        self.store = PersonaMemoryStore(db_path=db_path)
        self.embedder = EmbeddingProvider(model=embedding_model)
        self.llm_model = llm_model
        self.memory_top_k = memory_top_k
        self._llm_client = None

    @property
    def llm(self):
        if self._llm_client is None:
            from openai import OpenAI
            self._llm_client = OpenAI()
        return self._llm_client

    # ── Persona lifecycle ─────────────────────────────────────────────────────

    def create(
        self,
        name: str,
        system_prompt: str = "",
        traits: Optional[Dict] = None,
        persona_id: Optional[str] = None,
    ) -> Dict:
        """
        Create a new Persona.

        Parameters
        ----------
        name          : Human-readable name (e.g. "Alice")
        system_prompt : The identity instruction sent to the LLM at every turn.
                        If empty, a sensible default is generated.
        traits        : Optional dict of personality traits, e.g.
                        {"tone": "formal", "expertise": "cybersecurity"}
        persona_id    : Optional explicit ID; auto-generated if omitted.
        """
        pid = persona_id or str(uuid.uuid4())
        if not system_prompt:
            system_prompt = self._default_system_prompt(name, traits or {})
        persona = self.store.create_persona(
            persona_id=pid,
            name=name,
            system_prompt=system_prompt,
            traits=traits or {},
        )
        logger.info(f"Created persona '{name}' (id={pid})")
        return persona

    def get(self, persona_id: str) -> Optional[Dict]:
        """Retrieve a Persona by ID."""
        return self.store.get_persona(persona_id)

    def list(self) -> List[Dict]:
        """List all Personas."""
        return self.store.list_personas()

    def update(self, persona_id: str, **kwargs) -> Optional[Dict]:
        """Update Persona fields (name, system_prompt, traits)."""
        return self.store.update_persona(persona_id, **kwargs)

    def delete(self, persona_id: str):
        """Delete a Persona and all its memories."""
        self.store.delete_persona(persona_id)
        logger.info(f"Deleted persona {persona_id}")

    # ── Data alignment (feed) ─────────────────────────────────────────────────

    def feed(
        self,
        persona_id: str,
        content: str,
        source: str = "manual",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> int:
        """
        Feed text data to a Persona to align its knowledge base.

        The content is split into overlapping chunks, each embedded and stored
        as a 'knowledge' memory. At chat time, the most relevant chunks are
        automatically injected into the LLM context.

        Returns the number of chunks stored.
        """
        persona = self.store.get_persona(persona_id)
        if persona is None:
            raise ValueError(f"Persona not found: {persona_id}")

        chunks = self._chunk_text(content, chunk_size=chunk_size, overlap=chunk_overlap)
        embeddings = self.embedder.embed_batch(chunks)

        for chunk, emb in zip(chunks, embeddings):
            entry = MemoryEntry(
                memory_id=self._make_id(persona_id + chunk),
                persona_id=persona_id,
                content=chunk,
                embedding=emb,
                memory_type="knowledge",
                metadata={"source": source},
                importance=1.2,   # Knowledge memories are weighted higher
            )
            self.store.add_memory(entry)

        logger.info(f"Fed {len(chunks)} chunks to persona {persona_id} (source={source})")
        return len(chunks)

    def feed_file(self, persona_id: str, file_path: str) -> int:
        """Read a text file and feed its contents to the Persona."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return self.feed(persona_id, content, source=file_path)

    # ── Chat ──────────────────────────────────────────────────────────────────

    def chat(
        self,
        persona_id: str,
        user_message: str,
        session_id: Optional[str] = None,
        extra_context: Optional[str] = None,
    ) -> Dict:
        """
        Send a message to a Persona and receive a reply.

        The method:
          1. Embeds the user message
          2. Retrieves the top-K most relevant memories (conversation + knowledge)
          3. Builds a context-enriched prompt
          4. Calls the LLM
          5. Stores the exchange as a new conversation memory

        Returns a dict with:
          reply         : str — the Persona's response
          memories_used : int — how many memories were injected
          persona_name  : str
        """
        persona = self.store.get_persona(persona_id)
        if persona is None:
            raise ValueError(f"Persona not found: {persona_id}")

        # Embed the query
        query_emb = self.embedder.embed(user_message)

        # Retrieve relevant memories
        relevant = self.store.search_memories(
            persona_id=persona_id,
            query_embedding=query_emb,
            top_k=self.memory_top_k,
        )

        # Build messages
        messages = self._build_messages(
            persona=persona,
            user_message=user_message,
            relevant_memories=relevant,
            extra_context=extra_context,
        )

        # Call LLM
        try:
            response = self.llm.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM error: {e}")
            reply = f"[Error: {e}]"

        # Store this exchange as a conversation memory
        exchange_text = f"User: {user_message}\n{persona['name']}: {reply}"
        exchange_emb = self.embedder.embed(exchange_text)
        self.store.add_memory(MemoryEntry(
            memory_id=self._make_id(persona_id + exchange_text),
            persona_id=persona_id,
            content=exchange_text,
            embedding=exchange_emb,
            memory_type="conversation",
            metadata={"session_id": session_id or "default"},
            importance=1.0,
        ))

        return {
            "reply": reply,
            "persona_name": persona["name"],
            "memories_used": len(relevant),
            "persona_id": persona_id,
        }

    # ── Memory inspection ─────────────────────────────────────────────────────

    def memory_stats(self, persona_id: str) -> Dict:
        """Return memory statistics for a Persona."""
        all_mem = self.store.get_all_memories(persona_id)
        by_type: Dict[str, int] = {}
        for m in all_mem:
            by_type[m.memory_type] = by_type.get(m.memory_type, 0) + 1
        return {
            "persona_id": persona_id,
            "total_memories": len(all_mem),
            "by_type": by_type,
        }

    def recall(
        self,
        persona_id: str,
        query: str,
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Manually query a Persona's memory for the most relevant entries.
        Useful for debugging and inspection.
        """
        query_emb = self.embedder.embed(query)
        results = self.store.search_memories(
            persona_id=persona_id,
            query_embedding=query_emb,
            top_k=top_k,
        )
        return [
            {**entry.to_dict(), "similarity": round(score, 4)}
            for entry, score in results
        ]

    def clear_memory(self, persona_id: str, memory_type: Optional[str] = None):
        """Clear memories for a Persona (optionally filtered by type)."""
        self.store.clear_memories(persona_id, memory_type=memory_type)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _default_system_prompt(self, name: str, traits: Dict) -> str:
        trait_str = ""
        if traits:
            trait_str = " ".join(f"You are {v} in terms of {k}." for k, v in traits.items())
        return (
            f"You are {name}, a personal AI assistant. "
            f"{trait_str} "
            "You have access to a long-term memory of past conversations and knowledge "
            "that will be provided to you as context. Use this memory to give consistent, "
            "personalised responses. If a memory is relevant, reference it naturally. "
            "Never fabricate information — if you don't know something, say so."
        )

    def _build_messages(
        self,
        persona: Dict,
        user_message: str,
        relevant_memories: List[Tuple],
        extra_context: Optional[str],
    ) -> List[Dict]:
        """Construct the OpenAI messages array."""
        system = persona["system_prompt"]

        # Inject memories into the system message
        if relevant_memories:
            memory_block = "\n\n".join(
                f"[Memory {i+1} | similarity={score:.2f}]\n{entry.content}"
                for i, (entry, score) in enumerate(relevant_memories)
            )
            system += (
                "\n\n---\n"
                "RELEVANT MEMORIES (from your long-term memory store):\n"
                f"{memory_block}\n"
                "---\n"
                "Use the above memories as context for your response. "
                "Do not repeat them verbatim unless directly asked."
            )

        if extra_context:
            system += f"\n\nADDITIONAL CONTEXT:\n{extra_context}"

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ]

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks by word count."""
        words = text.split()
        if not words:
            return []
        chunks = []
        step = max(1, chunk_size - overlap)
        for i in range(0, len(words), step):
            chunk = " ".join(words[i : i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    @staticmethod
    def _make_id(seed: str) -> str:
        return hashlib.sha256(seed.encode()).hexdigest()[:32]

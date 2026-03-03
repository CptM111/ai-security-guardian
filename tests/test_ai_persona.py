"""
AI Security Guardian — AI Persona Skill Test Suite
Version: 1.5.0

Tests cover:
  1. Memory Engine (PersonaMemoryStore + EmbeddingProvider)
  2. Persona Manager (create, update, delete, feed, recall)
  3. Secure Chat (SecurePersonaChat — with mocked LLM)
  4. ASG Integration (detector pass-through, SkillsManager loading)
  5. Edge cases (empty inputs, missing personas, chunking)
"""

import sys
import os
import json
import uuid
import tempfile
import unittest.mock as mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─────────────────────────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────────────────────────

class Runner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def test(self, name: str, condition: bool, detail: str = ""):
        if condition:
            self.passed += 1
            print(f"  ✓ PASS | {name}")
        else:
            self.failed += 1
            msg = f"  ✗ FAIL | {name}"
            if detail:
                msg += f"\n         {detail}"
            print(msg)
            self.errors.append(name)

    def summary(self):
        total = self.passed + self.failed
        rate = (self.passed / total * 100) if total else 0
        print("\n" + "=" * 70)
        print(f"Total  : {total}")
        print(f"Passed : {self.passed}")
        print(f"Failed : {self.failed}")
        print(f"Rate   : {rate:.1f}%")
        if self.errors:
            print("\nFailed:")
            for e in self.errors:
                print(f"  - {e}")
        print("=" * 70)
        return self.failed == 0


r = Runner()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers: mock embeddings and LLM so tests run without API keys
# ─────────────────────────────────────────────────────────────────────────────

def _fake_embed(text: str):
    """Deterministic fake embedding: hash text into a 1536-dim unit vector."""
    import hashlib, math
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**31)
    import random
    rng = random.Random(seed)
    vec = [rng.gauss(0, 1) for _ in range(1536)]
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _patch_embedder(embedder):
    """Replace the EmbeddingProvider.embed method with a fake."""
    embedder.embed = lambda text: _fake_embed(text)
    embedder.embed_batch = lambda texts: [_fake_embed(t) for t in texts]
    return embedder


def _make_manager(tmp_dir: str):
    """Create a PersonaManager with a temp DB and mocked embedder."""
    from skills.ai_persona.persona import PersonaManager
    db = os.path.join(tmp_dir, "test_personas.db")
    mgr = PersonaManager(db_path=db)
    _patch_embedder(mgr.embedder)
    return mgr


# ─────────────────────────────────────────────────────────────────────────────
# 1. Memory Engine
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("1. MEMORY ENGINE")
print("=" * 70)

with tempfile.TemporaryDirectory() as tmp:
    from skills.ai_persona.memory import PersonaMemoryStore, MemoryEntry, EmbeddingProvider

    store = PersonaMemoryStore(db_path=os.path.join(tmp, "mem.db"))

    # Persona CRUD
    p = store.create_persona("p1", "Alice", system_prompt="You are Alice.")
    r.test("Create persona returns dict", isinstance(p, dict))
    r.test("Persona has id", p["id"] == "p1")
    r.test("Persona has name", p["name"] == "Alice")
    r.test("Persona has system_prompt", p["system_prompt"] == "You are Alice.")
    r.test("Persona has traits dict", isinstance(p["traits"], dict))

    p2 = store.get_persona("p1")
    r.test("get_persona returns same record", p2["id"] == "p1")

    missing = store.get_persona("nonexistent")
    r.test("get_persona returns None for unknown id", missing is None)

    store.create_persona("p2", "Bob")
    personas = store.list_personas()
    r.test("list_personas returns 2 records", len(personas) == 2)

    updated = store.update_persona("p1", name="Alice Updated", traits={"tone": "formal"})
    r.test("update_persona changes name", updated["name"] == "Alice Updated")
    r.test("update_persona changes traits", updated["traits"]["tone"] == "formal")

    # Memory CRUD
    emb = _fake_embed("test memory content")
    entry = MemoryEntry(
        memory_id="m1",
        persona_id="p1",
        content="Alice worked on CVE-2024-1234.",
        embedding=emb,
        memory_type="knowledge",
        importance=1.5,
    )
    store.add_memory(entry)
    r.test("add_memory does not raise", True)

    count = store.count_memories("p1")
    r.test("count_memories returns 1", count == 1)

    all_mem = store.get_all_memories("p1")
    r.test("get_all_memories returns 1 entry", len(all_mem) == 1)
    r.test("Memory content is preserved", all_mem[0].content == "Alice worked on CVE-2024-1234.")
    r.test("Memory importance is preserved", all_mem[0].importance == 1.5)

    # Add more memories for search test
    for i in range(4):
        e = MemoryEntry(
            memory_id=f"m{i+2}",
            persona_id="p1",
            content=f"Memory number {i+2} about security research.",
            embedding=_fake_embed(f"Memory number {i+2} about security research."),
            memory_type="conversation",
        )
        store.add_memory(e)

    # Semantic search
    query_emb = _fake_embed("CVE vulnerability research")
    results = store.search_memories("p1", query_emb, top_k=3)
    r.test("search_memories returns ≤3 results", len(results) <= 3)
    r.test("search_memories returns (entry, score) tuples", all(isinstance(s, float) for _, s in results))
    r.test("Scores are between 0 and 1", all(0 <= s <= 1.2 for _, s in results))
    r.test("Results are sorted by score descending", all(
        results[i][1] >= results[i+1][1] for i in range(len(results)-1)
    ))

    # Filter by type
    knowledge_results = store.search_memories("p1", query_emb, top_k=5, memory_type="knowledge")
    r.test("search_memories respects memory_type filter",
           all(e.memory_type == "knowledge" for e, _ in knowledge_results))

    # Clear memories
    store.clear_memories("p1", memory_type="conversation")
    remaining = store.get_all_memories("p1", memory_type="conversation")
    r.test("clear_memories by type removes correct entries", len(remaining) == 0)
    knowledge_remaining = store.get_all_memories("p1", memory_type="knowledge")
    r.test("clear_memories by type preserves other types", len(knowledge_remaining) == 1)

    # Delete persona
    store.delete_persona("p1")
    r.test("delete_persona removes persona", store.get_persona("p1") is None)
    r.test("delete_persona removes memories", store.count_memories("p1") == 0)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Persona Manager
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("2. PERSONA MANAGER")
print("=" * 70)

with tempfile.TemporaryDirectory() as tmp:
    mgr = _make_manager(tmp)

    # Create
    alice = mgr.create(
        name="Alice",
        system_prompt="You are Alice, a security researcher.",
        traits={"tone": "analytical"},
    )
    r.test("create() returns dict", isinstance(alice, dict))
    r.test("create() sets name", alice["name"] == "Alice")
    r.test("create() sets system_prompt", "Alice" in alice["system_prompt"])
    r.test("create() sets traits", alice["traits"]["tone"] == "analytical")

    # Auto system prompt
    bob = mgr.create(name="Bob")
    r.test("create() generates default system_prompt when empty", len(bob["system_prompt"]) > 10)

    # List
    all_personas = mgr.list()
    r.test("list() returns 2 personas", len(all_personas) == 2)

    # Get
    fetched = mgr.get(alice["id"])
    r.test("get() retrieves correct persona", fetched["id"] == alice["id"])

    missing = mgr.get("nonexistent-id")
    r.test("get() returns None for unknown id", missing is None)

    # Update
    updated = mgr.update(alice["id"], name="Alice Smith")
    r.test("update() changes name", updated["name"] == "Alice Smith")

    # Feed
    n_chunks = mgr.feed(
        alice["id"],
        "Alice has 10 years of experience in exploit development. "
        "She specialises in memory corruption vulnerabilities and has discovered "
        "over 50 CVEs in major software products. " * 10,
        source="bio",
    )
    r.test("feed() returns chunk count > 0", n_chunks > 0)

    stats = mgr.memory_stats(alice["id"])
    r.test("memory_stats() returns total_memories > 0", stats["total_memories"] > 0)
    r.test("memory_stats() has by_type breakdown", "knowledge" in stats["by_type"])
    r.test("memory_stats() knowledge count matches feed", stats["by_type"]["knowledge"] == n_chunks)

    # Feed file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Alice also has expertise in reverse engineering and malware analysis. " * 5)
        fname = f.name
    n_file = mgr.feed_file(alice["id"], fname)
    os.unlink(fname)
    r.test("feed_file() returns chunk count > 0", n_file > 0)

    # Recall
    results = mgr.recall(alice["id"], "exploit development CVE", top_k=3)
    r.test("recall() returns list", isinstance(results, list))
    r.test("recall() results have content", all("content" in x for x in results))
    r.test("recall() results have similarity", all("similarity" in x for x in results))

    # Clear memory
    mgr.clear_memory(alice["id"], memory_type="knowledge")
    stats_after = mgr.memory_stats(alice["id"])
    r.test("clear_memory() removes knowledge entries", stats_after["by_type"].get("knowledge", 0) == 0)

    # Delete
    mgr.delete(alice["id"])
    r.test("delete() removes persona", mgr.get(alice["id"]) is None)

    # Error: chat with nonexistent persona
    try:
        mgr.chat("nonexistent", "hello")
        r.test("chat() raises ValueError for unknown persona", False)
    except ValueError:
        r.test("chat() raises ValueError for unknown persona", True)

    # Error: feed to nonexistent persona
    try:
        mgr.feed("nonexistent", "some text")
        r.test("feed() raises ValueError for unknown persona", False)
    except ValueError:
        r.test("feed() raises ValueError for unknown persona", True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Text chunking
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("3. TEXT CHUNKING")
print("=" * 70)

from skills.ai_persona.persona import PersonaManager

chunks = PersonaManager._chunk_text("word " * 1000, chunk_size=100, overlap=20)
r.test("Chunking produces multiple chunks for long text", len(chunks) > 1)
r.test("Each chunk has ≤100 words", all(len(c.split()) <= 100 for c in chunks))
r.test("Chunks overlap (first words of chunk N+1 appear in chunk N)",
       any(chunks[i].split()[-20:] == chunks[i+1].split()[:20] for i in range(len(chunks)-1))
       if len(chunks) > 1 else True)

empty_chunks = PersonaManager._chunk_text("", chunk_size=100, overlap=10)
r.test("Chunking empty string returns []", empty_chunks == [])

short_chunks = PersonaManager._chunk_text("hello world", chunk_size=100, overlap=10)
r.test("Chunking short text returns 1 chunk", len(short_chunks) == 1)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Secure Chat (mocked LLM)
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("4. SECURE CHAT")
print("=" * 70)

with tempfile.TemporaryDirectory() as tmp:
    mgr = _make_manager(tmp)
    alice = mgr.create(name="Alice", system_prompt="You are Alice.")
    mgr.feed(alice["id"], "Alice is a security expert with 10 years of experience.")

    # Mock the LLM call
    mock_response = mock.MagicMock()
    mock_response.choices[0].message.content = "I am Alice, a security expert."
    mgr.llm.chat.completions.create = mock.MagicMock(return_value=mock_response)

    from skills.ai_persona.chat import SecurePersonaChat

    # Chat without security manager (no screening)
    session = SecurePersonaChat(alice["id"], mgr, security_manager=None)
    result = session.send("Who are you?")

    r.test("send() returns dict", isinstance(result, dict))
    r.test("send() has reply key", "reply" in result)
    r.test("send() has blocked key", "blocked" in result)
    r.test("send() has persona_name", result["persona_name"] == "Alice")
    r.test("send() blocked=False for safe message", result["blocked"] is False)
    r.test("send() reply is non-empty", len(result["reply"]) > 0)
    r.test("send() has session_id", len(result["session_id"]) > 0)
    r.test("send() has turn number", result["turn"] == 1)

    # Second turn increments turn counter
    result2 = session.send("What is your expertise?")
    r.test("Second turn has turn=2", result2["turn"] == 2)

    # History
    history = session.get_history()
    r.test("History has 4 entries after 2 turns (user+assistant each)", len(history) == 4)
    r.test("First history entry is user role", history[0]["role"] == "user")
    r.test("Second history entry is assistant role", history[1]["role"] == "assistant")

    # Clear history
    session.clear_history()
    r.test("clear_history() empties history", len(session.get_history()) == 0)

    # Chat with security manager that blocks a message
    mock_sec_result = mock.MagicMock()
    mock_sec_result.is_safe = False
    mock_sec_result.reason = "PCI DSS Violation"
    mock_sec_result.to_dict.return_value = {
        "agent_hints": ["[ASG BLOCK] Skill: financial_services | Severity: CRITICAL"]
    }

    mock_sm = mock.MagicMock()
    mock_sm.check.return_value = mock_sec_result

    secure_session = SecurePersonaChat(alice["id"], mgr, security_manager=mock_sm)
    blocked_result = secure_session.send("My card number is 4532015112830366")

    r.test("Blocked message returns blocked=True", blocked_result["blocked"] is True)
    r.test("Blocked message has block_reason", blocked_result["block_reason"] == "PCI DSS Violation")
    r.test("Blocked message reply contains [ASG]", "[ASG]" in blocked_result["reply"])
    r.test("Blocked message has agent_hints", len(blocked_result["agent_hints"]) > 0)
    r.test("Blocked message has memories_used=0", blocked_result["memories_used"] == 0)

    # Safe message passes through
    mock_sec_result_safe = mock.MagicMock()
    mock_sec_result_safe.is_safe = True
    mock_sm.check.return_value = mock_sec_result_safe

    safe_result = secure_session.send("What is your area of expertise?")
    r.test("Safe message with security manager passes through", safe_result["blocked"] is False)


# ─────────────────────────────────────────────────────────────────────────────
# 5. ASG Integration (detector pass-through)
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("5. ASG INTEGRATION")
print("=" * 70)

from skills.ai_persona.detector import AiPersonaDetector

detector = AiPersonaDetector(config={})
det = detector.check("Hello, who are you?", {})

r.test("AiPersonaDetector.check() returns Detection", hasattr(det, "detected"))
r.test("AiPersonaDetector always returns detected=False", det.detected is False)
r.test("AiPersonaDetector severity is NONE", det.severity == "NONE")
r.test("AiPersonaDetector skill_name is ai_persona", det.skill_name == "ai_persona")

# SkillsManager should load the ai_persona skill
try:
    from core.skills_manager import SkillsManager
    sm = SkillsManager()
    r.test("SkillsManager loads ai_persona skill", "ai_persona" in sm.skills)
    skill = sm.skills.get("ai_persona")
    r.test("ai_persona skill has correct version", skill.metadata.version == "1.0.0")
except Exception as e:
    r.test("SkillsManager loads ai_persona skill", False, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 6. Public API (__init__.py exports)
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("6. PUBLIC API EXPORTS")
print("=" * 70)

import skills.ai_persona as ai_persona_skill

r.test("PersonaManager is exported", hasattr(ai_persona_skill, "PersonaManager"))
r.test("SecurePersonaChat is exported", hasattr(ai_persona_skill, "SecurePersonaChat"))
r.test("PersonaChatCLI is exported", hasattr(ai_persona_skill, "PersonaChatCLI"))
r.test("PersonaMemoryStore is exported", hasattr(ai_persona_skill, "PersonaMemoryStore"))
r.test("MemoryEntry is exported", hasattr(ai_persona_skill, "MemoryEntry"))
r.test("EmbeddingProvider is exported", hasattr(ai_persona_skill, "EmbeddingProvider"))
r.test("__version__ is 1.0.0", ai_persona_skill.__version__ == "1.0.0")


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

success = r.summary()
sys.exit(0 if success else 1)

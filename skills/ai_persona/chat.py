"""
AI Security Guardian — AI Persona Skill
Secure Chat Interface

Every user message passes through ASG's security layer before reaching the
Persona. If a threat is detected, the message is blocked and the user receives
a structured rejection hint instead of an LLM response.

This creates a "security-first AI avatar":
  User Input → ASG Security Check → PersonaManager.chat() → Reply

Version: 1.0.0
"""

import logging
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)


class SecurePersonaChat:
    """
    A secure chat session bound to a single Persona.

    The session maintains a lightweight in-memory turn history for
    multi-turn coherence (separate from the persistent long-term memory).
    """

    def __init__(
        self,
        persona_id: str,
        persona_manager,          # PersonaManager instance
        security_manager=None,    # SkillsManager instance (optional)
        session_id: Optional[str] = None,
    ):
        import uuid
        self.persona_id = persona_id
        self.pm = persona_manager
        self.sm = security_manager
        self.session_id = session_id or str(uuid.uuid4())
        self.history: List[Dict] = []   # [{role, content, blocked}]
        self._persona_cache: Optional[Dict] = None

    @property
    def persona(self) -> Dict:
        if self._persona_cache is None:
            self._persona_cache = self.pm.get(self.persona_id)
            if self._persona_cache is None:
                raise ValueError(f"Persona not found: {self.persona_id}")
        return self._persona_cache

    def send(self, user_message: str) -> Dict:
        """
        Send a message to the Persona.

        Returns
        -------
        {
          "reply"         : str,
          "persona_name"  : str,
          "blocked"       : bool,
          "block_reason"  : str | None,
          "agent_hints"   : list[str],
          "memories_used" : int,
          "session_id"    : str,
          "turn"          : int,
        }
        """
        # Turn is based on user messages only (not assistant replies)
        user_turns = sum(1 for h in self.history if h["role"] == "user")
        turn = user_turns + 1

        # ── Security screening ────────────────────────────────────────────────
        block_reason = None
        agent_hints: List[str] = []

        if self.sm is not None:
            try:
                sec_result = self.sm.check(
                    user_message,
                    context={"session_id": self.session_id, "persona_id": self.persona_id},
                )
                if not sec_result.is_safe:
                    block_reason = sec_result.reason
                    d = sec_result.to_dict()
                    agent_hints = d.get("agent_hints", [])
                    self.history.append({
                        "role": "user",
                        "content": user_message,
                        "blocked": True,
                        "block_reason": block_reason,
                    })
                    return {
                        "reply": (
                            f"[ASG] Your message was blocked by the security layer.\n"
                            f"Reason: {block_reason}\n"
                            + (f"Hint: {agent_hints[0]}" if agent_hints else "")
                        ),
                        "persona_name": self.persona.get("name", "Persona"),
                        "blocked": True,
                        "block_reason": block_reason,
                        "agent_hints": agent_hints,
                        "memories_used": 0,
                        "session_id": self.session_id,
                        "turn": turn,
                    }
            except Exception as e:
                logger.warning(f"Security check failed (non-blocking): {e}")

        # ── Persona chat ──────────────────────────────────────────────────────
        result = self.pm.chat(
            persona_id=self.persona_id,
            user_message=user_message,
            session_id=self.session_id,
        )

        self.history.append({"role": "user", "content": user_message, "blocked": False})
        self.history.append({"role": "assistant", "content": result["reply"], "blocked": False})

        return {
            "reply": result["reply"],
            "persona_name": result["persona_name"],
            "blocked": False,
            "block_reason": None,
            "agent_hints": [],
            "memories_used": result.get("memories_used", 0),
            "session_id": self.session_id,
            "turn": turn,
        }

    def get_history(self) -> List[Dict]:
        """Return the in-session turn history."""
        return self.history

    def clear_history(self):
        """Clear the in-session turn history (does not affect long-term memory)."""
        self.history = []


class PersonaChatCLI:
    """
    Interactive command-line chat interface for testing Personas.

    Usage
    -----
    from skills.ai_persona.chat import PersonaChatCLI
    cli = PersonaChatCLI()
    cli.run()
    """

    COMMANDS = {
        "/help":    "Show this help message",
        "/list":    "List all Personas",
        "/create":  "Create a new Persona interactively",
        "/switch":  "Switch to a different Persona",
        "/feed":    "Feed text to the current Persona",
        "/recall":  "Query the Persona's memory",
        "/stats":   "Show memory statistics",
        "/history": "Show session history",
        "/clear":   "Clear session history",
        "/quit":    "Exit the chat",
    }

    def __init__(self, db_path: Optional[str] = None, enable_security: bool = True):
        from .persona import PersonaManager
        self.pm = PersonaManager(db_path=db_path)
        self.sm = None
        if enable_security:
            try:
                import sys, os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
                from core.skills_manager import SkillsManager
                self.sm = SkillsManager()
            except Exception as e:
                logger.warning(f"Could not load SkillsManager: {e}")
        self.current_session: Optional[SecurePersonaChat] = None

    def run(self):
        """Start the interactive CLI."""
        print("\n" + "=" * 60)
        print("  AI Security Guardian — Persona Chat")
        print("  Type /help for commands, /quit to exit")
        print("=" * 60)

        personas = self.pm.list()
        if personas:
            print(f"\n{len(personas)} existing Persona(s) found.")
            self._cmd_list()
            pid = input("\nEnter Persona ID to chat with (or press Enter to create new): ").strip()
            if pid:
                self._start_session(pid)
        else:
            print("\nNo Personas found. Let's create one.")
            self._cmd_create()

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not user_input:
                continue

            if user_input.startswith("/"):
                if not self._handle_command(user_input):
                    break
                continue

            if self.current_session is None:
                print("No active Persona. Use /create or /switch.")
                continue

            result = self.current_session.send(user_input)
            prefix = f"[{result['persona_name']}]"
            if result["blocked"]:
                print(f"\n{prefix} [BLOCKED]: {result['reply']}")
            else:
                print(f"\n{prefix}: {result['reply']}")
                if result["memories_used"] > 0:
                    print(f"  (recalled {result['memories_used']} memories)")

    def _handle_command(self, cmd: str) -> bool:
        """Returns False when the user wants to quit."""
        parts = cmd.split(None, 1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if command == "/quit":
            print("Goodbye!")
            return False
        elif command == "/help":
            self._cmd_help()
        elif command == "/list":
            self._cmd_list()
        elif command == "/create":
            self._cmd_create()
        elif command == "/switch":
            self._cmd_switch(arg)
        elif command == "/feed":
            self._cmd_feed(arg)
        elif command == "/recall":
            self._cmd_recall(arg)
        elif command == "/stats":
            self._cmd_stats()
        elif command == "/history":
            self._cmd_history()
        elif command == "/clear":
            self._cmd_clear()
        else:
            print(f"Unknown command: {command}. Type /help for available commands.")
        return True

    def _cmd_help(self):
        print("\nAvailable commands:")
        for cmd, desc in self.COMMANDS.items():
            print(f"  {cmd:<12} {desc}")

    def _cmd_list(self):
        personas = self.pm.list()
        if not personas:
            print("No Personas found.")
            return
        print("\nPersonas:")
        for p in personas:
            print(f"  {p['id'][:8]}...  {p['name']:<20}  created: {p['created_at'][:10]}")

    def _cmd_create(self):
        name = input("Persona name: ").strip()
        if not name:
            print("Name cannot be empty.")
            return
        print("System prompt (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        system_prompt = "\n".join(lines[:-1]).strip()
        persona = self.pm.create(name=name, system_prompt=system_prompt or "")
        print(f"Created Persona '{name}' (id={persona['id'][:8]}...)")
        self._start_session(persona["id"])

    def _cmd_switch(self, pid: str):
        if not pid:
            self._cmd_list()
            pid = input("Enter Persona ID: ").strip()
        self._start_session(pid)

    def _cmd_feed(self, text: str):
        if self.current_session is None:
            print("No active Persona.")
            return
        if not text:
            print("Enter text to feed (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            text = "\n".join(lines[:-1]).strip()
        if text:
            n = self.pm.feed(self.current_session.persona_id, text)
            print(f"Fed {n} chunk(s) to {self.current_session.persona['name']}.")

    def _cmd_recall(self, query: str):
        if self.current_session is None:
            print("No active Persona.")
            return
        if not query:
            query = input("Recall query: ").strip()
        results = self.pm.recall(self.current_session.persona_id, query, top_k=3)
        if not results:
            print("No relevant memories found.")
            return
        print(f"\nTop {len(results)} memories:")
        for i, r in enumerate(results, 1):
            print(f"\n  [{i}] similarity={r['similarity']} | type={r['memory_type']}")
            print(f"      {r['content'][:200]}{'...' if len(r['content']) > 200 else ''}")

    def _cmd_stats(self):
        if self.current_session is None:
            print("No active Persona.")
            return
        stats = self.pm.memory_stats(self.current_session.persona_id)
        print(f"\nMemory stats for '{self.current_session.persona['name']}':")
        print(f"  Total memories : {stats['total_memories']}")
        for t, n in stats["by_type"].items():
            print(f"  {t:<20}: {n}")

    def _cmd_history(self):
        if self.current_session is None:
            print("No active Persona.")
            return
        history = self.current_session.get_history()
        if not history:
            print("No history in this session.")
            return
        for turn in history:
            role = "You" if turn["role"] == "user" else self.current_session.persona["name"]
            blocked = " [BLOCKED]" if turn.get("blocked") else ""
            print(f"\n{role}{blocked}: {turn['content'][:300]}")

    def _cmd_clear(self):
        if self.current_session:
            self.current_session.clear_history()
            print("Session history cleared.")

    def _start_session(self, persona_id: str):
        persona = self.pm.get(persona_id)
        if persona is None:
            print(f"Persona not found: {persona_id}")
            return
        self.current_session = SecurePersonaChat(
            persona_id=persona_id,
            persona_manager=self.pm,
            security_manager=self.sm,
        )
        stats = self.pm.memory_stats(persona_id)
        print(f"\nNow chatting with '{persona['name']}' "
              f"({stats['total_memories']} memories loaded).")

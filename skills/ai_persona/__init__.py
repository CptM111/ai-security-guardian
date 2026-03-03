"""
AI Security Guardian — AI Persona Skill
Public API

Quick start
-----------
from skills.ai_persona import PersonaManager, SecurePersonaChat

mgr = PersonaManager()

# Create a persona
alice = mgr.create(
    name="Alice",
    system_prompt="You are Alice, a senior cybersecurity researcher...",
    traits={"tone": "analytical", "expertise": "zero-day research"},
)

# Align Alice with domain knowledge
mgr.feed(alice["id"], "Alice has 10 years of experience in exploit development...")

# Chat with Alice (with ASG security screening)
from core.skills_manager import SkillsManager
asg = SkillsManager()

session = SecurePersonaChat(alice["id"], mgr, security_manager=asg)
result = session.send("What is your area of expertise?")
print(result["reply"])
"""

from .persona import PersonaManager
from .chat import SecurePersonaChat, PersonaChatCLI
from .memory import PersonaMemoryStore, MemoryEntry, EmbeddingProvider

__all__ = [
    "PersonaManager",
    "SecurePersonaChat",
    "PersonaChatCLI",
    "PersonaMemoryStore",
    "MemoryEntry",
    "EmbeddingProvider",
]

__version__ = "1.0.0"

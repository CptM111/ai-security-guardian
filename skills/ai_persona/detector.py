"""
AI Security Guardian — AI Persona Skill
Detector: ASG Skills-compatible interface

The AI Persona skill is a *feature* module, not a threat detector.
Its detector always returns detected=False (pass-through), ensuring
it does not interfere with the security pipeline.

The actual Persona functionality is accessed via the PersonaManager
and SecurePersonaChat APIs directly.

Version: 1.0.0
"""

import sys
import os
from typing import Dict, Any

# Ensure the project root is on the path so core imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.base_detector import BaseDetector, Detection


class AiPersonaDetector(BaseDetector):
    """
    Pass-through detector for the AI Persona skill.

    This detector never flags a threat — it exists solely to satisfy
    the ASG Skills interface so that the ai_persona skill can be
    loaded by the SkillsManager alongside security-focused skills.

    All Persona functionality is exposed through the public API:
      from skills.ai_persona import PersonaManager, SecurePersonaChat
    """

    def check(self, text: str, context: Dict[str, Any]) -> Detection:
        return Detection(
            detected=False,
            skill_name="ai_persona",
            threat_type="none",
            confidence=0.0,
            severity="NONE",
            details="AI Persona skill: pass-through (feature module, not a threat detector)",
            matches=[],
        )

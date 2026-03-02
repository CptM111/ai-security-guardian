"""
AI Security Guardian - Rejection Log
Version: 1.4.1

Structured, machine-readable rejection logs that expose exactly why a prompt
was blocked. Designed to close the feedback loop between ASG and AI agents,
enabling agents to learn what crosses the line and how to rephrase safely.

Architecture Note:
    When ASG blocks a prompt, the RejectionLog surfaces:
      - which Skill triggered the block
      - the confidence score of the detection
      - the specific rule or pattern that matched
      - a human-readable explanation
      - an optional rewording suggestion for the agent

This allows downstream agents and developers to:
    1. Understand the exact reason for rejection (not just "blocked")
    2. Distinguish between a hard security violation vs. a borderline case
    3. Automatically rephrase or escalate based on severity
    4. Audit and improve their own prompts over time
"""

from __future__ import annotations

import json
import uuid
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RuleMatch:
    """
    A single rule or pattern that contributed to a rejection.

    Attributes:
        rule_id:     Machine-readable identifier for the rule (e.g. "PCI-PAN-001").
        rule_name:   Human-readable rule name (e.g. "Primary Account Number").
        pattern:     The regex / keyword / heuristic that matched (redacted if sensitive).
        matched_text: The fragment of the input that triggered the rule (truncated
                      and partially masked for privacy).
        framework:   Compliance framework this rule maps to, if any (e.g. "PCI DSS 4.0.1").
    """
    rule_id: str
    rule_name: str
    pattern: str
    matched_text: str = ""
    framework: str = ""


@dataclass
class RejectionEntry:
    """
    A single, fully-structured rejection log entry.

    This is the primary artifact produced by ASG when a prompt is blocked.
    It is designed to be both human-readable and machine-parseable so that
    AI agents can consume it programmatically.

    Attributes:
        rejection_id:   Unique UUID for this rejection event.
        timestamp:      ISO-8601 UTC timestamp of the rejection.
        skill_name:     The Skill that triggered the block (e.g. "financial_services").
        skill_version:  Version of the Skill at the time of detection.
        threat_type:    High-level threat category (e.g. "PCI DSS Violation").
        threat_subtype: Specific sub-category (e.g. "Primary Account Number (PAN)").
        severity:       CRITICAL | HIGH | MEDIUM | LOW
        confidence:     Float [0.0, 1.0] — how certain the detector is.
        rule_matches:   List of RuleMatch objects that fired.
        input_preview:  First 120 chars of the input (truncated for brevity).
        explanation:    Plain-English explanation of why this was blocked.
        suggestion:     Optional rewording hint for the agent.
        metadata:       Arbitrary key-value pairs for extensibility.
    """
    rejection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    skill_name: str = ""
    skill_version: str = ""
    threat_type: str = ""
    threat_subtype: str = ""
    severity: str = "NONE"
    confidence: float = 0.0
    rule_matches: List[RuleMatch] = field(default_factory=list)
    input_preview: str = ""
    explanation: str = ""
    suggestion: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain dict (JSON-serialisable)."""
        d = asdict(self)
        return d

    def to_json(self, indent: int = 2) -> str:
        """Return a pretty-printed JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_agent_hint(self) -> str:
        """
        Return a compact, single-string hint suitable for injecting into an
        agent's context window so it can understand and correct its output.

        Example output:
            [ASG BLOCK] Skill: financial_services | Rule: PCI-PAN-001
            Reason: Primary Account Number detected (confidence: 0.98, severity: CRITICAL)
            Suggestion: Remove or mask the card number before submitting.
        """
        lines = [
            f"[ASG BLOCK] Skill: {self.skill_name} | Severity: {self.severity} | "
            f"Confidence: {self.confidence:.0%}",
            f"Reason: {self.explanation}",
        ]
        if self.rule_matches:
            rule_ids = ", ".join(r.rule_id for r in self.rule_matches)
            lines.append(f"Rules triggered: {rule_ids}")
        if self.suggestion:
            lines.append(f"Suggestion: {self.suggestion}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# In-memory store (swap for a DB-backed store in production)
# ---------------------------------------------------------------------------

class RejectionLogStore:
    """
    Thread-safe in-memory store for RejectionEntry objects.

    In production, subclass this and override ``append`` / ``query`` to
    persist entries to PostgreSQL, Elasticsearch, or any other backend.
    """

    def __init__(self, max_entries: int = 10_000):
        self._entries: List[RejectionEntry] = []
        self._max_entries = max_entries

    def append(self, entry: RejectionEntry) -> None:
        """Persist a new rejection entry."""
        if len(self._entries) >= self._max_entries:
            # Rolling window — drop oldest
            self._entries = self._entries[-(self._max_entries - 1):]
        self._entries.append(entry)
        logger.debug(
            "RejectionLog: %s | skill=%s | severity=%s | confidence=%.2f",
            entry.rejection_id,
            entry.skill_name,
            entry.severity,
            entry.confidence,
        )

    def query(
        self,
        *,
        skill_name: Optional[str] = None,
        severity: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 100,
    ) -> List[RejectionEntry]:
        """Filter and return entries matching the given criteria."""
        results = self._entries
        if skill_name:
            results = [e for e in results if e.skill_name == skill_name]
        if severity:
            results = [e for e in results if e.severity == severity]
        if min_confidence > 0.0:
            results = [e for e in results if e.confidence >= min_confidence]
        return results[-limit:]

    def get(self, rejection_id: str) -> Optional[RejectionEntry]:
        """Fetch a single entry by its rejection_id."""
        for entry in reversed(self._entries):
            if entry.rejection_id == rejection_id:
                return entry
        return None

    def stats(self) -> Dict[str, Any]:
        """Return aggregate statistics over all stored entries."""
        if not self._entries:
            return {"total": 0}

        by_skill: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        confidence_sum = 0.0

        for e in self._entries:
            by_skill[e.skill_name] = by_skill.get(e.skill_name, 0) + 1
            by_severity[e.severity] = by_severity.get(e.severity, 0) + 1
            confidence_sum += e.confidence

        return {
            "total": len(self._entries),
            "by_skill": by_skill,
            "by_severity": by_severity,
            "avg_confidence": round(confidence_sum / len(self._entries), 4),
        }

    def clear(self) -> None:
        """Wipe all stored entries (useful in tests)."""
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)


# ---------------------------------------------------------------------------
# Builder — converts a Detection into a RejectionEntry
# ---------------------------------------------------------------------------

class RejectionLogBuilder:
    """
    Converts a raw ``Detection`` result (from any Skill) into a fully
    populated ``RejectionEntry`` with human-readable explanations and
    agent-friendly rewording suggestions.
    """

    # Maps threat_type → plain-English explanation template
    _EXPLANATIONS: Dict[str, str] = {
        "PCI DSS Violation": (
            "This prompt contains payment card data that is prohibited under "
            "PCI DSS 4.0.1. Storing, transmitting, or logging raw cardholder "
            "data in AI prompts creates a compliance violation."
        ),
        "Banking Data": (
            "Sensitive banking identifiers (account numbers, routing numbers, "
            "SWIFT/BIC codes, or IBAN) were detected. Exposing these to an AI "
            "model may constitute a GLBA or data-privacy violation."
        ),
        "Fraud Pattern": (
            "The prompt matches known financial fraud patterns, including "
            "social engineering, money laundering structuring, or wire fraud "
            "instruction changes."
        ),
        "Compliance Violation": (
            "The prompt references regulated financial data or processes in a "
            "way that may violate applicable compliance frameworks (PCI DSS, "
            "GLBA, SOX)."
        ),
        "Smart Contract Vulnerability": (
            "The prompt appears to request generation or analysis of code "
            "containing known smart contract vulnerabilities (OWASP SC Top 10)."
        ),
        "DeFi Attack": (
            "The prompt describes or requests assistance with a DeFi attack "
            "vector, including flash loan exploits or oracle manipulation."
        ),
        "Crypto Key Leakage": (
            "A private key, seed phrase, or exchange API secret was detected. "
            "These credentials must never be passed to an AI model."
        ),
        "Prompt Injection": (
            "The input contains patterns consistent with a prompt injection "
            "attack, attempting to override the model's system instructions."
        ),
    }

    # Maps threat_type → rewording suggestion for agents
    _SUGGESTIONS: Dict[str, str] = {
        "PCI DSS Violation": (
            "Replace the full card number with a masked version (e.g., "
            "4532-****-****-0366) or a tokenised reference before submitting."
        ),
        "Banking Data": (
            "Use an opaque reference ID instead of raw account or routing "
            "numbers. If you need to discuss a specific account, use the last "
            "4 digits only (e.g., 'account ending in 4321')."
        ),
        "Fraud Pattern": (
            "Rephrase the request to focus on legitimate use cases. If you are "
            "building a fraud-detection system, provide context that clarifies "
            "the educational or defensive intent."
        ),
        "Compliance Violation": (
            "Add context to clarify the legitimate purpose (e.g., 'For "
            "compliance audit purposes, explain how PCI DSS Requirement 3 "
            "applies to…'). Avoid including raw sensitive data."
        ),
        "Smart Contract Vulnerability": (
            "Frame the request as a security audit or educational query. For "
            "example: 'Identify and explain the reentrancy vulnerability in "
            "this code snippet' rather than requesting exploit code."
        ),
        "DeFi Attack": (
            "Reframe as a defensive security question: 'How can a protocol "
            "protect against flash loan attacks?' rather than requesting "
            "step-by-step attack instructions."
        ),
        "Crypto Key Leakage": (
            "Never include private keys or seed phrases in prompts. Use a "
            "placeholder (e.g., '<PRIVATE_KEY>') and handle the actual secret "
            "outside the AI context."
        ),
        "Prompt Injection": (
            "Remove any instruction-override patterns (e.g., 'Ignore previous "
            "instructions…') and rephrase as a direct, honest request."
        ),
    }

    @classmethod
    def from_detection(
        cls,
        detection,  # core.base_detector.Detection
        input_text: str,
        skill_version: str = "unknown",
    ) -> RejectionEntry:
        """
        Build a RejectionEntry from a Detection object.

        Args:
            detection:     The Detection result from a Skill's check() method.
            input_text:    The original input text (used to build the preview).
            skill_version: Version string of the Skill that produced the detection.

        Returns:
            A fully populated RejectionEntry.
        """
        # Build rule matches from the detection's matches list
        rule_matches = cls._build_rule_matches(detection)

        # Truncate and sanitise input preview
        preview = cls._safe_preview(input_text)

        # Look up explanation and suggestion
        threat_key = detection.threat_type or ""
        explanation = cls._EXPLANATIONS.get(
            threat_key,
            f"A security threat of type '{threat_key}' was detected in the prompt."
        )
        suggestion = cls._SUGGESTIONS.get(
            threat_key,
            "Review the prompt for sensitive data or policy-violating content "
            "and rephrase accordingly."
        )

        # Extract subtype from matches if available
        subtype = ""
        if detection.matches:
            first = detection.matches[0] if isinstance(detection.matches[0], dict) else {}
            subtype = first.get("subtype", "")

        return RejectionEntry(
            skill_name=detection.skill_name,
            skill_version=skill_version,
            threat_type=detection.threat_type,
            threat_subtype=subtype,
            severity=detection.severity,
            confidence=round(detection.confidence, 4),
            rule_matches=rule_matches,
            input_preview=preview,
            explanation=explanation,
            suggestion=suggestion,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_preview(text: str, max_len: int = 120) -> str:
        """Return a truncated, whitespace-normalised preview of the input."""
        cleaned = " ".join(text.split())
        if len(cleaned) > max_len:
            return cleaned[:max_len] + "…"
        return cleaned

    @staticmethod
    def _build_rule_matches(detection) -> List[RuleMatch]:
        """Convert raw match dicts from a Detection into RuleMatch objects."""
        matches = []
        if not detection.matches:
            return matches

        for i, m in enumerate(detection.matches):
            if isinstance(m, dict):
                matches.append(RuleMatch(
                    rule_id=m.get("rule_id", f"{detection.skill_name.upper()}-{i+1:03d}"),
                    rule_name=m.get("type", m.get("subtype", "Unknown Rule")),
                    pattern=m.get("pattern", ""),
                    matched_text=m.get("matched_text", ""),
                    framework=m.get("framework", ""),
                ))
            else:
                # Fallback for plain string matches
                matches.append(RuleMatch(
                    rule_id=f"{detection.skill_name.upper()}-{i+1:03d}",
                    rule_name=str(m),
                    pattern="",
                ))
        return matches


# ---------------------------------------------------------------------------
# Module-level singleton store
# ---------------------------------------------------------------------------

_store = RejectionLogStore()


def get_store() -> RejectionLogStore:
    """Return the module-level singleton RejectionLogStore."""
    return _store

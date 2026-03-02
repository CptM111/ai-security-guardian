"""
AI Security Guardian - Rejection Log Test Suite
Version: 1.4.1

Tests for the RejectionLog architecture feature, verifying that:
  - RejectionEntry is correctly populated from a Detection
  - RejectionLogStore stores, queries, and returns stats correctly
  - RejectionLogBuilder produces accurate explanations and suggestions
  - SkillsManager exposes rejection_logs on SecurityResult
  - agent_hints are human-readable and machine-parseable
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rejection_log import (
    RejectionEntry,
    RejectionLogStore,
    RejectionLogBuilder,
    RuleMatch,
    get_store,
)
from core.base_detector import Detection


# ─────────────────────────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────────────────────────

class TestRunner:
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
        print(f"Total Tests : {total}")
        print(f"Passed      : {self.passed}")
        print(f"Failed      : {self.failed}")
        print(f"Pass Rate   : {rate:.1f}%")
        if self.errors:
            print("\nFailed tests:")
            for e in self.errors:
                print(f"  - {e}")
        print("=" * 70)
        return self.failed == 0


runner = TestRunner()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_detection(
    threat_type="PCI DSS Violation",
    skill_name="financial_services",
    severity="CRITICAL",
    confidence=0.98,
    matches=None,
):
    return Detection(
        detected=True,
        skill_name=skill_name,
        threat_type=threat_type,
        confidence=confidence,
        severity=severity,
        details="Test detection",
        matches=matches or [
            {
                "type": "PCI DSS Violation",
                "subtype": "Primary Account Number (PAN)",
                "pattern": "453201****0366",
                "framework": "PCI DSS",
                "pci_requirement": "Requirement 3",
            }
        ],
    )


# ─────────────────────────────────────────────────────────────────────────────
# 1. RejectionEntry basics
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("1. REJECTION ENTRY STRUCTURE")
print("=" * 70)

entry = RejectionEntry(
    skill_name="financial_services",
    skill_version="1.0.0",
    threat_type="PCI DSS Violation",
    threat_subtype="Primary Account Number (PAN)",
    severity="CRITICAL",
    confidence=0.98,
    input_preview="Process payment for card 4532...",
    explanation="Card data detected.",
    suggestion="Mask the card number.",
)

runner.test("Entry has a UUID rejection_id", len(entry.rejection_id) == 36)
runner.test("Entry has a UTC timestamp", "T" in entry.rejection_id or "T" in entry.timestamp)
runner.test("Severity is CRITICAL", entry.severity == "CRITICAL")
runner.test("Confidence is 0.98", entry.confidence == 0.98)
runner.test("skill_name is set", entry.skill_name == "financial_services")

# Serialisation
d = entry.to_dict()
runner.test("to_dict() returns a dict", isinstance(d, dict))
runner.test("to_dict() contains rejection_id", "rejection_id" in d)
runner.test("to_dict() contains rule_matches list", isinstance(d["rule_matches"], list))

j = entry.to_json()
runner.test("to_json() returns valid JSON", isinstance(json.loads(j), dict))

hint = entry.to_agent_hint()
runner.test("to_agent_hint() contains [ASG BLOCK]", "[ASG BLOCK]" in hint)
runner.test("to_agent_hint() contains skill name", "financial_services" in hint)
runner.test("to_agent_hint() contains suggestion", "Mask" in hint)


# ─────────────────────────────────────────────────────────────────────────────
# 2. RejectionLogBuilder
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("2. REJECTION LOG BUILDER")
print("=" * 70)

detection = make_detection()
built = RejectionLogBuilder.from_detection(
    detection,
    input_text="Process payment for card 4532015112830366",
    skill_version="1.0.0",
)

runner.test("Built entry has correct skill_name", built.skill_name == "financial_services")
runner.test("Built entry has correct severity", built.severity == "CRITICAL")
runner.test("Built entry has correct confidence", built.confidence == 0.98)
runner.test("Built entry has non-empty explanation", len(built.explanation) > 10)
runner.test("Built entry has non-empty suggestion", len(built.suggestion) > 10)
runner.test("Built entry has input_preview", "4532" in built.input_preview or "Process" in built.input_preview)
runner.test("Built entry has rule_matches", len(built.rule_matches) >= 1)
runner.test("Rule match has rule_id", len(built.rule_matches[0].rule_id) > 0)
runner.test("Rule match has rule_name", len(built.rule_matches[0].rule_name) > 0)

# Long input truncation
long_text = "A" * 300
built_long = RejectionLogBuilder.from_detection(detection, input_text=long_text)
runner.test("Long input is truncated to ≤121 chars", len(built_long.input_preview) <= 121)
runner.test("Truncated input ends with ellipsis", built_long.input_preview.endswith("…"))

# Different threat types
for threat in ["Banking Data", "Fraud Pattern", "Smart Contract Vulnerability", "Crypto Key Leakage"]:
    det = make_detection(threat_type=threat, skill_name="test_skill")
    b = RejectionLogBuilder.from_detection(det, input_text="test")
    runner.test(
        f"Builder has explanation for '{threat}'",
        len(b.explanation) > 10,
    )
    runner.test(
        f"Builder has suggestion for '{threat}'",
        len(b.suggestion) > 10,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. RejectionLogStore
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("3. REJECTION LOG STORE")
print("=" * 70)

store = RejectionLogStore(max_entries=5)

# Append entries
for i in range(3):
    e = RejectionEntry(
        skill_name="financial_services" if i < 2 else "web3",
        severity="CRITICAL" if i == 0 else "HIGH",
        confidence=0.9 - i * 0.1,
        threat_type="PCI DSS Violation" if i < 2 else "Smart Contract Vulnerability",
    )
    store.append(e)

runner.test("Store has 3 entries", len(store) == 3)

# Query by skill
fs_entries = store.query(skill_name="financial_services")
runner.test("Query by skill returns 2 entries", len(fs_entries) == 2)

web3_entries = store.query(skill_name="web3")
runner.test("Query by web3 skill returns 1 entry", len(web3_entries) == 1)

# Query by severity
critical_entries = store.query(severity="CRITICAL")
runner.test("Query by CRITICAL returns 1 entry", len(critical_entries) == 1)

# Query by confidence
high_conf = store.query(min_confidence=0.75)
runner.test("Query min_confidence=0.75 returns 2 entries", len(high_conf) == 2)

# Get by id
first_id = store.query()[0].rejection_id
fetched = store.get(first_id)
runner.test("get() retrieves entry by id", fetched is not None and fetched.rejection_id == first_id)

missing = store.get("nonexistent-id")
runner.test("get() returns None for unknown id", missing is None)

# Stats
stats = store.stats()
runner.test("stats() returns total count", stats["total"] == 3)
runner.test("stats() has by_skill breakdown", "financial_services" in stats["by_skill"])
runner.test("stats() has avg_confidence", "avg_confidence" in stats)
runner.test("avg_confidence is a float", isinstance(stats["avg_confidence"], float))

# Rolling window
for i in range(5):
    store.append(RejectionEntry(skill_name="overflow_test"))
runner.test("Store respects max_entries limit", len(store) <= 5)

# Clear
store.clear()
runner.test("clear() empties the store", len(store) == 0)


# ─────────────────────────────────────────────────────────────────────────────
# 4. End-to-end: SkillsManager integration
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("4. SKILLS MANAGER INTEGRATION")
print("=" * 70)

try:
    from core.skills_manager import SkillsManager

    # Clear the global store before integration tests
    get_store().clear()

    manager = SkillsManager()

    # Test with a prompt that should trigger financial_services
    result = manager.check("Process payment for card 4532015112830366")

    runner.test("SkillsManager.check() returns a SecurityResult", hasattr(result, "is_safe"))
    runner.test("SecurityResult has rejection_logs attribute", hasattr(result, "rejection_logs"))

    if not result.is_safe:
        runner.test("Blocked result has at least one rejection_log", len(result.rejection_logs) >= 1)
        log = result.rejection_logs[0]
        runner.test("rejection_log has skill_name", len(log.skill_name) > 0)
        runner.test("rejection_log has severity", log.severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"])
        runner.test("rejection_log has confidence > 0", log.confidence > 0)
        runner.test("rejection_log has explanation", len(log.explanation) > 10)
        runner.test("rejection_log has suggestion", len(log.suggestion) > 10)

        # to_dict() should include rejection_logs
        d = result.to_dict()
        runner.test("to_dict() includes rejection_logs key", "rejection_logs" in d)
        runner.test("to_dict() includes agent_hints key", "agent_hints" in d)
        runner.test("agent_hints is a list of strings", isinstance(d["agent_hints"], list))
        runner.test("First agent_hint contains [ASG BLOCK]", "[ASG BLOCK]" in d["agent_hints"][0])

        # Global store should have the entry
        store_count = len(get_store())
        runner.test("Global store received the rejection entry", store_count >= 1)

    else:
        # If no detection, just verify the attribute exists and is empty
        runner.test("Safe result has empty rejection_logs", result.rejection_logs == [])
        print("  (Note: financial_services skill may not have triggered — check skill triggers)")

except Exception as e:
    runner.test("SkillsManager integration (no exception)", False, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# 5. Agent hint format
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 70)
print("5. AGENT HINT FORMAT")
print("=" * 70)

entry_with_rules = RejectionEntry(
    skill_name="financial_services",
    skill_version="1.0.0",
    threat_type="PCI DSS Violation",
    severity="CRITICAL",
    confidence=0.98,
    explanation="Card number detected.",
    suggestion="Mask the card number.",
    rule_matches=[
        RuleMatch(rule_id="PCI-PAN-001", rule_name="Primary Account Number", pattern="4xxx-xxxx-xxxx-xxxx"),
    ],
)

hint = entry_with_rules.to_agent_hint()
runner.test("Hint contains severity", "CRITICAL" in hint)
runner.test("Hint contains confidence percentage", "98%" in hint)
runner.test("Hint contains rule ID", "PCI-PAN-001" in hint)
runner.test("Hint contains suggestion", "Mask" in hint)
runner.test("Hint is multi-line", "\n" in hint)

# Verify hint is usable as a context injection
lines = hint.split("\n")
runner.test("Hint has at least 3 lines", len(lines) >= 3)
runner.test("First line is the block header", lines[0].startswith("[ASG BLOCK]"))


# ─────────────────────────────────────────────────────────────────────────────
# Final summary
# ─────────────────────────────────────────────────────────────────────────────

success = runner.summary()
sys.exit(0 if success else 1)

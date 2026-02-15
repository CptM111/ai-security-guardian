"""
Prompt Firewall - LLM Prompt Injection Detection and Prevention

This component protects against:
- Prompt injection attacks (OWASP LLM01)
- Jailbreak attempts
- System prompt leakage
- Malicious instruction injection
"""
import re
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class PromptFirewall:
    """
    A specialized firewall for LLMs that inspects and sanitizes all incoming prompts
    to prevent injection attacks.
    """
    
    def __init__(self):
        """Initialize the Prompt Firewall with detection patterns"""
        self.injection_patterns = self._load_injection_patterns()
        self.jailbreak_patterns = self._load_jailbreak_patterns()
        self.system_leak_patterns = self._load_system_leak_patterns()
        
    def _load_injection_patterns(self) -> List[Dict[str, Any]]:
        """Load prompt injection detection patterns"""
        return [
            {
                "name": "ignore_previous_instructions",
                "pattern": r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
                "severity": "high",
                "confidence": 0.95
            },
            {
                "name": "override_instructions",
                "pattern": r"(override|disregard|forget)\s+(all\s+)?(previous|prior|system)\s+(instructions?|rules?|prompts?)",
                "severity": "high",
                "confidence": 0.95
            },
            {
                "name": "new_instructions",
                "pattern": r"(new|updated)\s+instructions?:?\s*",
                "severity": "medium",
                "confidence": 0.75
            },
            {
                "name": "role_manipulation",
                "pattern": r"(you\s+are\s+now|act\s+as|pretend\s+to\s+be|roleplay\s+as)\s+(a\s+)?\w+",
                "severity": "medium",
                "confidence": 0.70
            },
            {
                "name": "system_message_injection",
                "pattern": r"<\|?(system|assistant|user)\|?>",
                "severity": "high",
                "confidence": 0.90
            },
            {
                "name": "delimiter_escape",
                "pattern": r"(```|---|===|\*\*\*)\s*(system|instructions?|prompt)",
                "severity": "high",
                "confidence": 0.85
            }
        ]
    
    def _load_jailbreak_patterns(self) -> List[Dict[str, Any]]:
        """Load jailbreak attempt detection patterns"""
        return [
            {
                "name": "dan_jailbreak",
                "pattern": r"(do\s+anything\s+now|DAN\s+mode)",
                "severity": "critical",
                "confidence": 0.98
            },
            {
                "name": "hypothetical_scenario",
                "pattern": r"(imagine|hypothetically|in\s+a\s+fictional)\s+(world|scenario|universe)",
                "severity": "medium",
                "confidence": 0.65
            },
            {
                "name": "ethical_bypass",
                "pattern": r"(without\s+any\s+)?(ethical|moral|safety)\s+(constraints?|guidelines?|restrictions?)",
                "severity": "high",
                "confidence": 0.85
            },
            {
                "name": "developer_mode",
                "pattern": r"(developer|debug|admin|god)\s+mode",
                "severity": "high",
                "confidence": 0.90
            }
        ]
    
    def _load_system_leak_patterns(self) -> List[Dict[str, Any]]:
        """Load system prompt leakage detection patterns"""
        return [
            {
                "name": "reveal_instructions",
                "pattern": r"(show|reveal|display|tell\s+me)\s+(your\s+)?(system\s+)?(instructions?|prompts?|rules?)",
                "severity": "high",
                "confidence": 0.90
            },
            {
                "name": "repeat_above",
                "pattern": r"repeat\s+(everything\s+)?(above|before|prior)",
                "severity": "high",
                "confidence": 0.85
            },
            {
                "name": "print_instructions",
                "pattern": r"(print|output|echo)\s+(your\s+)?(system\s+)?(prompt|instructions?)",
                "severity": "high",
                "confidence": 0.90
            }
        ]
    
    def analyze(self, prompt: str, model_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a prompt for potential security threats.
        
        Args:
            prompt: The user prompt to analyze
            model_id: The target model identifier
            user_id: Optional user identifier for tracking
            
        Returns:
            Dictionary containing analysis results:
            - is_malicious: Boolean indicating if prompt is malicious
            - confidence: Confidence score (0.0 to 1.0)
            - attack_types: List of detected attack types
            - reason: Human-readable explanation
            - sanitized_prompt: Sanitized version (if applicable)
            - alert_id: Unique alert identifier
        """
        prompt_lower = prompt.lower()
        detected_attacks = []
        max_confidence = 0.0
        
        # Check injection patterns
        for pattern_def in self.injection_patterns:
            if re.search(pattern_def["pattern"], prompt_lower, re.IGNORECASE):
                detected_attacks.append({
                    "type": "prompt_injection",
                    "name": pattern_def["name"],
                    "severity": pattern_def["severity"],
                    "confidence": pattern_def["confidence"]
                })
                max_confidence = max(max_confidence, pattern_def["confidence"])
        
        # Check jailbreak patterns
        for pattern_def in self.jailbreak_patterns:
            if re.search(pattern_def["pattern"], prompt_lower, re.IGNORECASE):
                detected_attacks.append({
                    "type": "jailbreak",
                    "name": pattern_def["name"],
                    "severity": pattern_def["severity"],
                    "confidence": pattern_def["confidence"]
                })
                max_confidence = max(max_confidence, pattern_def["confidence"])
        
        # Check system leak patterns
        for pattern_def in self.system_leak_patterns:
            if re.search(pattern_def["pattern"], prompt_lower, re.IGNORECASE):
                detected_attacks.append({
                    "type": "system_leak",
                    "name": pattern_def["name"],
                    "severity": pattern_def["severity"],
                    "confidence": pattern_def["confidence"]
                })
                max_confidence = max(max_confidence, pattern_def["confidence"])
        
        # Additional heuristics
        if self._check_excessive_special_chars(prompt):
            detected_attacks.append({
                "type": "obfuscation",
                "name": "excessive_special_characters",
                "severity": "medium",
                "confidence": 0.60
            })
            max_confidence = max(max_confidence, 0.60)
        
        if self._check_encoding_tricks(prompt):
            detected_attacks.append({
                "type": "encoding_attack",
                "name": "encoding_obfuscation",
                "severity": "medium",
                "confidence": 0.65
            })
            max_confidence = max(max_confidence, 0.65)
        
        # Determine if malicious
        is_malicious = len(detected_attacks) > 0 and max_confidence >= 0.70
        
        # Generate alert if malicious
        alert_id = None
        if is_malicious:
            alert_id = self._generate_alert_id(prompt, model_id)
        
        # Build response
        result = {
            "is_malicious": is_malicious,
            "confidence": max_confidence,
            "attack_types": [attack["type"] for attack in detected_attacks],
            "attacks_detected": detected_attacks,
            "reason": self._generate_reason(detected_attacks) if is_malicious else None,
            "sanitized_prompt": self._sanitize_prompt(prompt) if not is_malicious else None,
            "alert_id": alert_id,
            "timestamp": datetime.utcnow().isoformat(),
            "model_id": model_id,
            "user_id": user_id
        }
        
        return result
    
    def _check_excessive_special_chars(self, prompt: str) -> bool:
        """Check for excessive special characters (potential obfuscation)"""
        special_chars = sum(1 for c in prompt if not c.isalnum() and not c.isspace())
        total_chars = len(prompt)
        if total_chars == 0:
            return False
        ratio = special_chars / total_chars
        return ratio > 0.3
    
    def _check_encoding_tricks(self, prompt: str) -> bool:
        """Check for encoding-based obfuscation"""
        # Check for hex encoding
        hex_pattern = r'(\\x[0-9a-fA-F]{2}){5,}'
        if re.search(hex_pattern, prompt):
            return True
        
        # Check for unicode escapes
        unicode_pattern = r'(\\u[0-9a-fA-F]{4}){3,}'
        if re.search(unicode_pattern, prompt):
            return True
        
        return False
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """
        Sanitize a prompt by removing potentially dangerous elements.
        Note: This is a basic implementation. In production, use more sophisticated methods.
        """
        # Remove special tokens
        sanitized = re.sub(r'<\|?(system|assistant|user)\|?>', '', prompt)
        
        # Remove excessive special characters
        sanitized = re.sub(r'[^\w\s.,!?-]', '', sanitized)
        
        return sanitized.strip()
    
    def _generate_reason(self, detected_attacks: List[Dict[str, Any]]) -> str:
        """Generate a human-readable explanation of detected threats"""
        if not detected_attacks:
            return "No threats detected"
        
        attack_types = set(attack["type"] for attack in detected_attacks)
        severity_levels = [attack["severity"] for attack in detected_attacks]
        
        highest_severity = "critical" if "critical" in severity_levels else \
                          "high" if "high" in severity_levels else \
                          "medium" if "medium" in severity_levels else "low"
        
        type_descriptions = {
            "prompt_injection": "Prompt Injection",
            "jailbreak": "Jailbreak Attempt",
            "system_leak": "System Prompt Leakage Attempt",
            "obfuscation": "Obfuscation Detected",
            "encoding_attack": "Encoding-based Attack"
        }
        
        detected_types = [type_descriptions.get(t, t) for t in attack_types]
        
        return f"{highest_severity.capitalize()} severity threat detected: {', '.join(detected_types)}"
    
    def _generate_alert_id(self, prompt: str, model_id: str) -> str:
        """Generate a unique alert identifier"""
        unique_string = f"{prompt}{model_id}{datetime.utcnow().isoformat()}"
        hash_digest = hashlib.sha256(unique_string.encode()).hexdigest()[:12]
        return f"alert-{hash_digest}"

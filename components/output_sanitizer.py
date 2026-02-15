"""
Output Sanitizer - LLM Output Validation and Sanitization

This component protects against:
- Cross-Site Scripting (XSS)
- SQL Injection
- Command Injection
- Sensitive data leakage
- Improper output handling (OWASP LLM05)
"""
import re
import html
from typing import Dict, List, Any, Optional
from datetime import datetime


class OutputSanitizer:
    """
    Inspects and sanitizes LLM outputs to prevent injection attacks and data leakage.
    """
    
    def __init__(self):
        """Initialize the Output Sanitizer with sanitization rules"""
        self.xss_patterns = self._load_xss_patterns()
        self.sql_patterns = self._load_sql_patterns()
        self.command_patterns = self._load_command_patterns()
        self.sensitive_patterns = self._load_sensitive_patterns()
        
    def _load_xss_patterns(self) -> List[Dict[str, Any]]:
        """Load XSS detection patterns"""
        return [
            {
                "name": "script_tag",
                "pattern": r"<script[^>]*>.*?</script>",
                "severity": "high"
            },
            {
                "name": "javascript_protocol",
                "pattern": r"javascript:",
                "severity": "high"
            },
            {
                "name": "on_event_handler",
                "pattern": r"on(load|error|click|mouse\w+|key\w+)\s*=",
                "severity": "high"
            },
            {
                "name": "iframe_tag",
                "pattern": r"<iframe[^>]*>",
                "severity": "medium"
            },
            {
                "name": "object_embed_tag",
                "pattern": r"<(object|embed)[^>]*>",
                "severity": "medium"
            }
        ]
    
    def _load_sql_patterns(self) -> List[Dict[str, Any]]:
        """Load SQL injection detection patterns"""
        return [
            {
                "name": "sql_comment",
                "pattern": r"(--|#|/\*|\*/)",
                "severity": "medium"
            },
            {
                "name": "sql_union",
                "pattern": r"\bUNION\s+(ALL\s+)?SELECT\b",
                "severity": "high"
            },
            {
                "name": "sql_injection_keywords",
                "pattern": r"\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE)\s+(TABLE|DATABASE|USER)\b",
                "severity": "high"
            },
            {
                "name": "sql_always_true",
                "pattern": r"(1\s*=\s*1|'1'\s*=\s*'1'|OR\s+1\s*=\s*1)",
                "severity": "high"
            }
        ]
    
    def _load_command_patterns(self) -> List[Dict[str, Any]]:
        """Load command injection detection patterns"""
        return [
            {
                "name": "shell_command",
                "pattern": r"(;|\||&|`|\$\()\s*(ls|cat|rm|wget|curl|bash|sh|python|perl|ruby)",
                "severity": "high"
            },
            {
                "name": "path_traversal",
                "pattern": r"\.\./|\.\.\\",
                "severity": "medium"
            }
        ]
    
    def _load_sensitive_patterns(self) -> List[Dict[str, Any]]:
        """Load sensitive data detection patterns"""
        return [
            {
                "name": "credit_card",
                "pattern": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
                "severity": "high",
                "redact": "XXXX-XXXX-XXXX-XXXX"
            },
            {
                "name": "ssn",
                "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
                "severity": "high",
                "redact": "XXX-XX-XXXX"
            },
            {
                "name": "email",
                "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "severity": "medium",
                "redact": "[EMAIL_REDACTED]"
            },
            {
                "name": "api_key",
                "pattern": r"\b(sk|pk|api)[-_][a-zA-Z0-9]{32,}\b",
                "severity": "critical",
                "redact": "[API_KEY_REDACTED]"
            },
            {
                "name": "aws_key",
                "pattern": r"\b(AKIA|ASIA)[A-Z0-9]{16}\b",
                "severity": "critical",
                "redact": "[AWS_KEY_REDACTED]"
            }
        ]
    
    def sanitize(self, content: str, context: str = "general") -> Dict[str, Any]:
        """
        Sanitize LLM output content based on context.
        
        Args:
            content: The output content to sanitize
            context: The context of the output (html, json, sql, general)
            
        Returns:
            Dictionary containing:
            - sanitized_content: The sanitized content
            - removed_elements: List of removed malicious elements
            - warnings: List of warnings about potential issues
            - redacted_items: List of redacted sensitive data types
        """
        sanitized = content
        removed_elements = []
        warnings = []
        redacted_items = []
        
        # Context-specific sanitization
        if context in ["html", "web", "web_response"]:
            sanitized, xss_removed = self._sanitize_xss(sanitized)
            removed_elements.extend(xss_removed)
        
        if context in ["sql", "database"]:
            sanitized, sql_removed = self._sanitize_sql(sanitized)
            removed_elements.extend(sql_removed)
            if sql_removed:
                warnings.append("Potential SQL injection patterns detected and removed")
        
        if context in ["shell", "command", "system"]:
            sanitized, cmd_removed = self._sanitize_commands(sanitized)
            removed_elements.extend(cmd_removed)
            if cmd_removed:
                warnings.append("Potential command injection patterns detected and removed")
        
        # Always check for sensitive data
        sanitized, redacted = self._redact_sensitive_data(sanitized)
        redacted_items.extend(redacted)
        if redacted:
            warnings.append(f"Sensitive data redacted: {', '.join(set(redacted))}")
        
        # General sanitization for all contexts
        if context == "html":
            sanitized = html.escape(sanitized)
        
        return {
            "sanitized_content": sanitized,
            "removed_elements": removed_elements,
            "warnings": warnings,
            "redacted_items": redacted_items,
            "original_length": len(content),
            "sanitized_length": len(sanitized),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _sanitize_xss(self, content: str) -> tuple[str, List[str]]:
        """Remove XSS attack vectors"""
        sanitized = content
        removed = []
        
        for pattern_def in self.xss_patterns:
            matches = re.findall(pattern_def["pattern"], sanitized, re.IGNORECASE | re.DOTALL)
            if matches:
                removed.extend([f"XSS:{pattern_def['name']}" for _ in matches])
                sanitized = re.sub(pattern_def["pattern"], "", sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        return sanitized, removed
    
    def _sanitize_sql(self, content: str) -> tuple[str, List[str]]:
        """Remove SQL injection patterns"""
        sanitized = content
        removed = []
        
        for pattern_def in self.sql_patterns:
            if pattern_def["severity"] == "high":
                matches = re.findall(pattern_def["pattern"], sanitized, re.IGNORECASE)
                if matches:
                    removed.extend([f"SQL:{pattern_def['name']}" for _ in matches])
                    sanitized = re.sub(pattern_def["pattern"], "", sanitized, flags=re.IGNORECASE)
        
        return sanitized, removed
    
    def _sanitize_commands(self, content: str) -> tuple[str, List[str]]:
        """Remove command injection patterns"""
        sanitized = content
        removed = []
        
        for pattern_def in self.command_patterns:
            matches = re.findall(pattern_def["pattern"], sanitized, re.IGNORECASE)
            if matches:
                removed.extend([f"CMD:{pattern_def['name']}" for _ in matches])
                sanitized = re.sub(pattern_def["pattern"], "", sanitized, flags=re.IGNORECASE)
        
        return sanitized, removed
    
    def _redact_sensitive_data(self, content: str) -> tuple[str, List[str]]:
        """Redact sensitive data from content"""
        sanitized = content
        redacted = []
        
        for pattern_def in self.sensitive_patterns:
            matches = re.findall(pattern_def["pattern"], sanitized, re.IGNORECASE)
            if matches:
                redacted.extend([pattern_def['name'] for _ in matches])
                sanitized = re.sub(
                    pattern_def["pattern"],
                    pattern_def.get("redact", "[REDACTED]"),
                    sanitized,
                    flags=re.IGNORECASE
                )
        
        return sanitized, redacted
    
    def validate_json_output(self, content: str) -> Dict[str, Any]:
        """Validate JSON output for security issues"""
        import json
        
        try:
            parsed = json.loads(content)
            
            # Check for deeply nested structures (potential DoS)
            max_depth = self._get_json_depth(parsed)
            if max_depth > 20:
                return {
                    "valid": False,
                    "error": "JSON structure too deeply nested",
                    "max_depth": max_depth
                }
            
            # Check for excessively large arrays
            if self._check_large_arrays(parsed, threshold=10000):
                return {
                    "valid": False,
                    "error": "JSON contains excessively large arrays"
                }
            
            return {
                "valid": True,
                "parsed": parsed
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"Invalid JSON: {str(e)}"
            }
    
    def _get_json_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate the maximum depth of a JSON structure"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._get_json_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._get_json_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def _check_large_arrays(self, obj: Any, threshold: int = 10000) -> bool:
        """Check if JSON contains arrays exceeding threshold"""
        if isinstance(obj, list):
            if len(obj) > threshold:
                return True
            return any(self._check_large_arrays(item, threshold) for item in obj)
        elif isinstance(obj, dict):
            return any(self._check_large_arrays(v, threshold) for v in obj.values())
        return False

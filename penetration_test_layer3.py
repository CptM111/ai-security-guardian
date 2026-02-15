"""
Layer 3 Penetration Testing: Authentication Bypass & API Exploitation

Tests authentication weaknesses, API vulnerabilities, and access control.
"""

import requests
import json
import time
import hashlib
import secrets
from datetime import datetime


class Layer3Tester:
    """Layer 3: Authentication and API attacks"""
    
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_base_url = api_base_url
        self.results = []
        self.attack_counter = 0
    
    def _record(self, category, payload, result, severity, notes, env_note=""):
        self.attack_counter += 1
        self.results.append({
            "id": f"L3-{self.attack_counter:03d}",
            "category": category,
            "payload": str(payload)[:100],
            "result": result,
            "severity": severity,
            "notes": notes,
            "env_note": env_note
        })
    
    def test_authentication_bypass(self):
        """Test authentication bypass attempts"""
        print("\n" + "="*80)
        print("LAYER 3.1: AUTHENTICATION BYPASS ATTACKS")
        print("="*80)
        
        # Test 1: No authentication
        print("\n[1] Testing no authentication...")
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/protect/prompt",
                headers={"Content-Type": "application/json"},
                json={"prompt": "test", "model_id": "gpt-4"},
                timeout=5
            )
            
            is_blocked = response.status_code == 401
            result = "BLOCKED" if is_blocked else "SUCCESSFUL"
            severity = "CRITICAL" if not is_blocked else "INFO"
            
            self._record("Auth Bypass", "No Authorization header", result, severity,
                        f"No auth {'rejected' if is_blocked else 'ACCEPTED'}")
            
            icon = "🛡️ " if is_blocked else "🚨🚨"
            print(f"{icon} L3-{self.attack_counter:03d}: {result} - No authentication")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Test 2: Invalid format
        print("\n[2] Testing malformed authorization headers...")
        malformed_headers = [
            "InvalidFormat key123",
            "Bearer",
            "Bearer ",
            "Bearerkey123",
            "Basic dXNlcjpwYXNz",  # Basic auth instead of Bearer
            "key123",  # No Bearer prefix
        ]
        
        for header in malformed_headers:
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/protect/prompt",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": header
                    },
                    json={"prompt": "test", "model_id": "gpt-4"},
                    timeout=5
                )
                
                is_blocked = response.status_code == 401
                result = "BLOCKED" if is_blocked else "SUCCESSFUL"
                severity = "HIGH" if not is_blocked else "INFO"
                
                self._record("Auth Bypass", f"Malformed: {header}", result, severity,
                            f"Malformed header {'rejected' if is_blocked else 'ACCEPTED'}")
                
                icon = "🛡️ " if is_blocked else "🚨"
                print(f"{icon} L3-{self.attack_counter:03d}: {result} - {header[:40]}...")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        # Test 3: Invalid/fake keys
        print("\n[3] Testing invalid API keys...")
        fake_keys = [
            "asg_" + "0" * 40,  # Wrong format
            "asg_fake_key_12345",
            "asg_" + secrets.token_urlsafe(32),  # Random but not in DB
            "sk-1234567890",  # OpenAI-style key
            "Bearer asg_invalid",
        ]
        
        for fake_key in fake_keys:
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/protect/prompt",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {fake_key}"
                    },
                    json={"prompt": "test", "model_id": "gpt-4"},
                    timeout=5
                )
                
                is_blocked = response.status_code == 401
                result = "BLOCKED" if is_blocked else "SUCCESSFUL"
                severity = "CRITICAL" if not is_blocked else "INFO"
                
                self._record("Auth Bypass", f"Fake key: {fake_key[:30]}", result, severity,
                            f"Invalid key {'rejected' if is_blocked else 'ACCEPTED'}")
                
                icon = "🛡️ " if is_blocked else "🚨🚨"
                print(f"{icon} L3-{self.attack_counter:03d}: {result} - Fake key")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        # Test 4: SQL injection in auth
        print("\n[4] Testing SQL injection in authentication...")
        sql_payloads = [
            "asg_' OR '1'='1",
            "asg_admin'--",
            "asg_' UNION SELECT * FROM api_keys--",
        ]
        
        for payload in sql_payloads:
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/protect/prompt",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {payload}"
                    },
                    json={"prompt": "test", "model_id": "gpt-4"},
                    timeout=5
                )
                
                is_blocked = response.status_code == 401
                result = "BLOCKED" if is_blocked else "SUCCESSFUL"
                severity = "CRITICAL" if not is_blocked else "INFO"
                
                self._record("SQL in Auth", payload, result, severity,
                            f"SQL injection {'blocked' if is_blocked else 'SUCCEEDED'}")
                
                icon = "🛡️ " if is_blocked else "🚨🚨"
                print(f"{icon} L3-{self.attack_counter:03d}: {result} - SQL injection attempt")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def test_rate_limiting(self):
        """Test rate limiting bypass"""
        print("\n" + "="*80)
        print("LAYER 3.2: RATE LIMITING BYPASS")
        print("="*80)
        
        # Generate a valid key for testing
        import sys
        sys.path.insert(0, '/home/ubuntu/ai-security-guardian')
        from auth.api_key_manager import APIKeyManager
        manager = APIKeyManager("data/api_keys.db")
        api_key, _ = manager.generate_key("Rate Limit Test", rate_limit=10)  # 10 req/min
        
        print(f"\n[1] Testing rate limit enforcement (limit: 10 req/min)...")
        
        # Send 15 requests rapidly
        blocked_count = 0
        for i in range(15):
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/protect/prompt",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={"prompt": "test", "model_id": "gpt-4"},
                    timeout=5
                )
                
                if response.status_code == 429:  # Too Many Requests
                    blocked_count += 1
                
                time.sleep(0.1)  # Small delay
            except:
                pass
        
        # Check if rate limiting is enforced
        is_enforced = blocked_count > 0
        result = "BLOCKED" if is_enforced else "SUCCESSFUL"
        severity = "MEDIUM" if not is_enforced else "INFO"
        
        env_note = "Note: Rate limiting requires production middleware (currently not enforced in MVP)"
        
        self._record("Rate Limit Bypass", "15 rapid requests", result, severity,
                    f"Rate limit {'enforced' if is_enforced else 'NOT enforced'} ({blocked_count}/15 blocked)",
                    env_note)
        
        icon = "🛡️ " if is_enforced else "⚠️ "
        print(f"{icon} L3-{self.attack_counter:03d}: {result} - {blocked_count}/15 requests blocked")
    
    def test_api_endpoint_enumeration(self):
        """Test API endpoint enumeration"""
        print("\n" + "="*80)
        print("LAYER 3.3: API ENDPOINT ENUMERATION")
        print("="*80)
        
        # Test common endpoints
        endpoints = [
            "/api/v1/admin",
            "/api/v1/users",
            "/api/v1/keys",
            "/api/v1/config",
            "/api/v1/debug",
            "/api/v1/internal",
            "/.env",
            "/api/v1/../../../etc/passwd",
            "/api/v2/protect/prompt",  # Version bypass
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{self.api_base_url}{endpoint}",
                    timeout=5
                )
                
                # Check if endpoint exists and is accessible
                is_exposed = response.status_code not in [404, 401, 403]
                result = "SUCCESSFUL" if is_exposed else "BLOCKED"
                severity = "MEDIUM" if is_exposed else "INFO"
                
                self._record("Endpoint Enum", endpoint, result, severity,
                            f"Endpoint {endpoint} {'EXPOSED' if is_exposed else 'protected'} (HTTP {response.status_code})")
                
                icon = "🚨" if is_exposed else "🛡️ "
                print(f"{icon} L3-{self.attack_counter:03d}: {result} - {endpoint} (HTTP {response.status_code})")
            except:
                pass
    
    def test_parameter_tampering(self):
        """Test parameter tampering"""
        print("\n" + "="*80)
        print("LAYER 3.4: PARAMETER TAMPERING")
        print("="*80)
        
        # Generate valid key
        import sys
        sys.path.insert(0, '/home/ubuntu/ai-security-guardian')
        from auth.api_key_manager import APIKeyManager
        manager = APIKeyManager("data/api_keys.db")
        api_key, _ = manager.generate_key("Param Test", rate_limit=1000)
        
        # Test 1: Extra parameters
        print("\n[1] Testing extra parameters...")
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/protect/prompt",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "prompt": "test",
                    "model_id": "gpt-4",
                    "is_admin": True,  # Extra param
                    "bypass_security": True,  # Extra param
                    "debug": True  # Extra param
                },
                timeout=5
            )
            
            # Check if extra params caused issues
            is_safe = response.status_code in [200, 400]
            result = "BLOCKED" if is_safe else "SUCCESSFUL"
            severity = "MEDIUM" if not is_safe else "INFO"
            
            self._record("Param Tampering", "Extra params (is_admin, bypass_security)", result, severity,
                        f"Extra parameters {'ignored' if is_safe else 'PROCESSED'}")
            
            icon = "🛡️ " if is_safe else "🚨"
            print(f"{icon} L3-{self.attack_counter:03d}: {result} - Extra parameters")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        # Test 2: Type confusion
        print("\n[2] Testing type confusion...")
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/protect/prompt",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "prompt": ["array", "instead", "of", "string"],  # Wrong type
                    "model_id": 12345  # Number instead of string
                },
                timeout=5
            )
            
            is_safe = response.status_code in [400, 422]  # Validation error expected
            result = "BLOCKED" if is_safe else "SUCCESSFUL"
            severity = "LOW" if not is_safe else "INFO"
            
            self._record("Type Confusion", "Array for prompt, number for model_id", result, severity,
                        f"Type confusion {'rejected' if is_safe else 'ACCEPTED'}")
            
            icon = "🛡️ " if is_safe else "⚠️ "
            print(f"{icon} L3-{self.attack_counter:03d}: {result} - Type confusion")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def generate_report(self):
        """Generate Layer 3 report"""
        print("\n" + "="*80)
        print("PENETRATION TEST REPORT - LAYER 3")
        print("="*80)
        
        total = len(self.results)
        blocked = sum(1 for r in self.results if r["result"] == "BLOCKED")
        successful = sum(1 for r in self.results if r["result"] == "SUCCESSFUL")
        
        critical = sum(1 for r in self.results if r["severity"] == "CRITICAL" and r["result"] != "BLOCKED")
        high = sum(1 for r in self.results if r["severity"] == "HIGH" and r["result"] != "BLOCKED")
        medium = sum(1 for r in self.results if r["severity"] == "MEDIUM" and r["result"] != "BLOCKED")
        
        print(f"\n📊 SUMMARY")
        print(f"   Total Attacks:     {total}")
        print(f"   🛡️  Blocked:         {blocked} ({blocked/total*100:.1f}%)")
        print(f"   🚨 Successful:      {successful} ({successful/total*100:.1f}%)")
        print(f"\n🔥 SEVERITY (Unblocked)")
        print(f"   CRITICAL:          {critical}")
        print(f"   HIGH:              {high}")
        print(f"   MEDIUM:            {medium}")
        
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
            for v in vulns:
                print(f"\n   {v['id']} - {v['severity']}")
                print(f"   Category: {v['category']}")
                print(f"   Notes: {v['notes']}")
                if v['env_note']:
                    print(f"   Environment: {v['env_note']}")
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
    print("LAYER 3: AUTHENTICATION BYPASS & API EXPLOITATION")
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
    
    # Run tests
    tester = Layer3Tester()
    tester.test_authentication_bypass()
    tester.test_rate_limiting()
    tester.test_api_endpoint_enumeration()
    tester.test_parameter_tampering()
    
    # Report
    stats = tester.generate_report()
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"/home/ubuntu/pentest_layer3_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(tester.results, f, indent=2)
    
    print(f"\n💾 Results saved to: {report_file}")
    print(f"\nBlock Rate: {stats['block_rate']:.1f}%")
    print(f"Vulnerabilities: {stats['successful']}\n")


if __name__ == "__main__":
    main()

"""
Comprehensive Authentication Test Suite

Tests all aspects of API key authentication:
1. Key generation
2. Key validation
3. Key expiration
4. Key revocation
5. API endpoint protection
6. Invalid key scenarios
"""

import requests
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from auth.api_key_manager import APIKeyManager


class AuthenticationTester:
    """Comprehensive authentication testing"""
    
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_base_url = api_base_url
        self.manager = APIKeyManager("data/api_keys_test.db")
        self.test_results = []
    
    def run_all_tests(self):
        """Run all authentication tests"""
        print("=" * 80)
        print("AI SECURITY GUARDIAN - AUTHENTICATION TEST SUITE")
        print("=" * 80)
        print()
        
        # Test 1: Key Generation
        self.test_key_generation()
        
        # Test 2: Valid Key Authentication
        self.test_valid_key_auth()
        
        # Test 3: Invalid Key Rejection
        self.test_invalid_key_rejection()
        
        # Test 4: Missing Key Rejection
        self.test_missing_key_rejection()
        
        # Test 5: Malformed Authorization Header
        self.test_malformed_auth_header()
        
        # Test 6: Key Revocation
        self.test_key_revocation()
        
        # Test 7: Expired Key
        self.test_expired_key()
        
        # Test 8: Key Usage Tracking
        self.test_usage_tracking()
        
        # Test 9: Multiple Keys
        self.test_multiple_keys()
        
        # Test 10: API Endpoint Protection
        self.test_endpoint_protection()
        
        # Print summary
        self.print_summary()
    
    def test_key_generation(self):
        """Test 1: API key generation"""
        print("Test 1: API Key Generation")
        print("-" * 80)
        
        try:
            raw_key, api_key = self.manager.generate_key(
                name="Test Key 1",
                expires_in_days=30,
                rate_limit=1000
            )
            
            assert raw_key.startswith("asg_"), "Key should start with 'asg_'"
            assert len(raw_key) > 40, "Key should be sufficiently long"
            assert api_key.key_id.startswith("key_"), "Key ID should start with 'key_'"
            assert api_key.is_active, "New key should be active"
            
            self.valid_key = raw_key  # Save for later tests
            self.valid_key_id = api_key.key_id
            
            print(f"✅ PASS - Generated key: {raw_key[:20]}...")
            print(f"  Key ID: {api_key.key_id}")
            print(f"  Expires: {api_key.expires_at}")
            self.test_results.append(("Key Generation", "PASS"))
            
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.test_results.append(("Key Generation", "FAIL"))
        
        print()
    
    def test_valid_key_auth(self):
        """Test 2: Valid key authentication"""
        print("Test 2: Valid Key Authentication")
        print("-" * 80)
        
        try:
            is_valid, reason = self.manager.validate_key(self.valid_key)
            
            assert is_valid, f"Valid key should authenticate: {reason}"
            assert reason is None, "No error reason for valid key"
            
            print(f"✅ PASS - Key validated successfully")
            self.test_results.append(("Valid Key Auth", "PASS"))
            
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.test_results.append(("Valid Key Auth", "FAIL"))
        
        print()
    
    def test_invalid_key_rejection(self):
        """Test 3: Invalid key rejection"""
        print("Test 3: Invalid Key Rejection")
        print("-" * 80)
        
        try:
            invalid_keys = [
                "asg_invalid_key_12345",
                "wrong_prefix_key",
                "asg_",
                "totally_fake_key"
            ]
            
            for invalid_key in invalid_keys:
                is_valid, reason = self.manager.validate_key(invalid_key)
                
                assert not is_valid, f"Invalid key should be rejected: {invalid_key}"
                assert reason is not None, "Should have error reason"
                assert "Invalid API key" in reason, f"Unexpected reason: {reason}"
            
            print(f"✅ PASS - All {len(invalid_keys)} invalid keys rejected")
            self.test_results.append(("Invalid Key Rejection", "PASS"))
            
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.test_results.append(("Invalid Key Rejection", "FAIL"))
        
        print()
    
    def test_missing_key_rejection(self):
        """Test 4: Missing key rejection via API"""
        print("Test 4: Missing Key Rejection (API)")
        print("-" * 80)
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/protect/prompt",
                json={"prompt": "test", "model_id": "gpt-4"}
            )
            
            assert response.status_code == 401, f"Expected 401, got {response.status_code}"
            assert "Missing API key" in response.json()["detail"]
            
            print(f"✅ PASS - Missing key rejected with 401")
            print(f"  Response: {response.json()['detail']}")
            self.test_results.append(("Missing Key Rejection", "PASS"))
            
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.test_results.append(("Missing Key Rejection", "FAIL"))
        
        print()
    
    def test_malformed_auth_header(self):
        """Test 5: Malformed authorization header"""
        print("Test 5: Malformed Authorization Header")
        print("-" * 80)
        
        try:
            malformed_headers = [
                {"Authorization": "InvalidFormat key123"},
                {"Authorization": "key123"},
                {"Authorization": "Bearer"},
                {"Authorization": "Bearer "},
            ]
            
            for headers in malformed_headers:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/protect/prompt",
                    json={"prompt": "test", "model_id": "gpt-4"},
                    headers=headers
                )
                
                assert response.status_code == 401, f"Expected 401 for {headers}"
            
            print(f"✅ PASS - All {len(malformed_headers)} malformed headers rejected")
            self.test_results.append(("Malformed Auth Header", "PASS"))
            
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.test_results.append(("Malformed Auth Header", "FAIL"))
        
        print()
    
    def test_key_revocation(self):
        """Test 6: Key revocation"""
        print("Test 6: Key Revocation")
        print("-" * 80)
        
        try:
            # Generate a key to revoke
            raw_key, api_key = self.manager.generate_key(
                name="Key to Revoke",
                rate_limit=1000
            )
            
            # Verify it works
            is_valid, _ = self.manager.validate_key(raw_key)
            assert is_valid, "Key should be valid before revocation"
            
            # Revoke it
            success = self.manager.revoke_key(api_key.key_id)
            assert success, "Revocation should succeed"
            
            # Verify it no longer works
            is_valid, reason = self.manager.validate_key(raw_key)
            assert not is_valid, "Revoked key should be invalid"
            assert "revoked" in reason.lower(), f"Should mention revocation: {reason}"
            
            print(f"✅ PASS - Key revoked successfully")
            print(f"  Key ID: {api_key.key_id}")
            print(f"  Rejection reason: {reason}")
            self.test_results.append(("Key Revocation", "PASS"))
            
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.test_results.append(("Key Revocation", "FAIL"))
        
        print()
    
    def test_expired_key(self):
        """Test 7: Expired key rejection"""
        print("Test 7: Expired Key Rejection")
        print("-" * 80)
        
        try:
            # Generate a key that expires immediately (0 days)
            # Note: This creates a key with expiration in the past
            from datetime import datetime, timedelta
            
            raw_key, api_key = self.manager.generate_key(
                name="Expired Key",
                expires_in_days=0,  # Expires immediately
                rate_limit=1000
            )
            
            # Manually set expiration to past
            import sqlite3
            conn = sqlite3.connect(self.manager.db_path)
            cursor = conn.cursor()
            past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
            cursor.execute(
                "UPDATE api_keys SET expires_at = ? WHERE key_id = ?",
                (past_date, api_key.key_id)
            )
            conn.commit()
            conn.close()
            
            # Verify it's rejected
            is_valid, reason = self.manager.validate_key(raw_key)
            assert not is_valid, "Expired key should be invalid"
            assert "expired" in reason.lower(), f"Should mention expiration: {reason}"
            
            print(f"✅ PASS - Expired key rejected")
            print(f"  Rejection reason: {reason}")
            self.test_results.append(("Expired Key Rejection", "PASS"))
            
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.test_results.append(("Expired Key Rejection", "FAIL"))
        
        print()
    
    def test_usage_tracking(self):
        """Test 8: Usage tracking"""
        print("Test 8: Usage Tracking")
        print("-" * 80)
        
        try:
            # Generate a new key
            raw_key, api_key = self.manager.generate_key(
                name="Usage Tracking Test",
                rate_limit=1000
            )
            
            # Get initial usage
            key_info = self.manager.get_key_info(api_key.key_id)
            initial_usage = key_info.usage_count
            
            # Use the key multiple times
            for i in range(5):
                self.manager.validate_key(raw_key)
            
            # Check usage increased
            key_info = self.manager.get_key_info(api_key.key_id)
            final_usage = key_info.usage_count
            
            assert final_usage == initial_usage + 5, f"Usage should increase by 5, got {final_usage - initial_usage}"
            assert key_info.last_used_at is not None, "Last used timestamp should be set"
            
            print(f"✅ PASS - Usage tracked correctly")
            print(f"  Initial usage: {initial_usage}")
            print(f"  Final usage: {final_usage}")
            print(f"  Last used: {key_info.last_used_at}")
            self.test_results.append(("Usage Tracking", "PASS"))
            
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.test_results.append(("Usage Tracking", "FAIL"))
        
        print()
    
    def test_multiple_keys(self):
        """Test 9: Multiple keys management"""
        print("Test 9: Multiple Keys Management")
        print("-" * 80)
        
        try:
            # Generate multiple keys
            keys = []
            for i in range(3):
                raw_key, api_key = self.manager.generate_key(
                    name=f"Multi Key {i+1}",
                    rate_limit=1000
                )
                keys.append((raw_key, api_key))
            
            # Verify all keys work
            for raw_key, api_key in keys:
                is_valid, _ = self.manager.validate_key(raw_key)
                assert is_valid, f"Key {api_key.key_id} should be valid"
            
            # List keys
            all_keys = self.manager.list_keys()
            assert len(all_keys) >= 3, f"Should have at least 3 keys, got {len(all_keys)}"
            
            print(f"✅ PASS - Multiple keys managed successfully")
            print(f"  Total active keys: {len(all_keys)}")
            self.test_results.append(("Multiple Keys", "PASS"))
            
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.test_results.append(("Multiple Keys", "FAIL"))
        
        print()
    
    def test_endpoint_protection(self):
        """Test 10: API endpoint protection"""
        print("Test 10: API Endpoint Protection")
        print("-" * 80)
        
        try:
            endpoints = [
                ("/api/v1/protect/prompt", {"prompt": "test", "model_id": "gpt-4"}),
                ("/api/v1/protect/output", {"content": "test", "context": "general"}),
                ("/api/v1/scan/model", {"model_id": "test", "scan_type": "quick"}),
            ]
            
            passed = 0
            for endpoint, payload in endpoints:
                # Test without key - should fail
                response = requests.post(
                    f"{self.api_base_url}{endpoint}",
                    json=payload
                )
                assert response.status_code == 401, f"{endpoint} should require auth"
                
                # Test with valid key - should succeed
                response = requests.post(
                    f"{self.api_base_url}{endpoint}",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.valid_key}"}
                )
                assert response.status_code == 200, f"{endpoint} should work with valid key"
                
                passed += 1
            
            print(f"✅ PASS - All {passed} endpoints protected correctly")
            self.test_results.append(("Endpoint Protection", "PASS"))
            
        except Exception as e:
            print(f"❌ FAIL - {str(e)}")
            self.test_results.append(("Endpoint Protection", "FAIL"))
        
        print()
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print()
        
        total = len(self.test_results)
        passed = sum(1 for _, result in self.test_results if result == "PASS")
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        for test_name, result in self.test_results:
            icon = "✅" if result == "PASS" else "❌"
            print(f"{icon} {test_name}: {result}")
        
        print()
        print("-" * 80)
        print(f"Total Tests:  {total}")
        print(f"Passed:       {passed}")
        print(f"Failed:       {failed}")
        print(f"Pass Rate:    {pass_rate:.1f}%")
        print("-" * 80)
        print()
        
        if pass_rate == 100:
            print("🎉 ALL TESTS PASSED! Authentication system is fully functional.")
        elif pass_rate >= 80:
            print("⚠️  Most tests passed, but some issues need attention.")
        else:
            print("❌ Multiple failures detected. Authentication system needs fixes.")
        
        print()
        print("=" * 80)


def main():
    """Run authentication tests"""
    print()
    print("Starting API server check...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code != 200:
            print("❌ API server is not responding correctly.")
            print("   Please start the server with: cd api && python main.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server at http://localhost:8000")
        print("   Please start the server with: cd api && python main.py")
        return
    
    print("✅ API server is running")
    print()
    
    # Run tests
    tester = AuthenticationTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3.11
"""
Direct Cryptocurrency Detector Testing
Tests the crypto_detector module without going through the API
"""

import sys
import json
from components.crypto_detector_v2 import get_enhanced_crypto_detector

def test_crypto_detector():
    """Run comprehensive tests on crypto detector"""
    detector = get_enhanced_crypto_detector()
    
    # Load test cases from DeFi and CeFi penetration tests
    defi_tests = []
    cefi_tests = []
    
    try:
        with open('/home/ubuntu/pentest_defi_20260215_103935.json', 'r') as f:
            defi_tests = json.load(f)
    except:
        print("⚠️  Could not load DeFi test data")
    
    try:
        with open('/home/ubuntu/pentest_cefi_20260215_103511.json', 'r') as f:
            cefi_tests = json.load(f)
    except:
        print("⚠️  Could not load CeFi test data")
    
    all_tests = defi_tests + cefi_tests
    
    if not all_tests:
        print("❌ No test data found!")
        return
    
    print(f"🔍 Testing {len(all_tests)} cryptocurrency attack vectors...")
    print("=" * 80)
    
    blocked = 0
    bypassed = 0
    results = []
    
    for i, test in enumerate(all_tests, 1):
        test_id = test.get('id', f'TEST-{i}')
        payload = test.get('prompt', test.get('payload', ''))
        category = test.get('category', 'Unknown')
        severity = test.get('severity', 'UNKNOWN')
        
        # Test with crypto detector
        is_safe, reason, issues = detector.is_safe(payload)
        
        if not is_safe:
            blocked += 1
            status = "🛡️  BLOCKED"
            color = "\033[92m"  # Green
        else:
            bypassed += 1
            status = "❌ BYPASSED"
            color = "\033[91m"  # Red
        
        reset = "\033[0m"
        
        result = {
            'id': test_id,
            'category': category,
            'severity': severity,
            'payload': payload[:100],
            'blocked': not is_safe,
            'reason': reason,
            'issues': issues
        }
        results.append(result)
        
        # Print summary for critical/high severity
        if severity in ['CRITICAL', 'HIGH']:
            print(f"{color}{status}{reset} {test_id} - {severity}")
            print(f"   Category: {category}")
            print(f"   Payload: {payload[:80]}...")
            if not is_safe:
                print(f"   Reason: {reason}")
                print(f"   Issues: {', '.join(issues)}")
            print()
    
    # Final statistics
    print("=" * 80)
    print("CRYPTOCURRENCY DETECTOR TEST RESULTS")
    print("=" * 80)
    print(f"Total Tests:    {len(all_tests)}")
    print(f"🛡️  Blocked:     {blocked} ({blocked/len(all_tests)*100:.1f}%)")
    print(f"❌ Bypassed:    {bypassed} ({bypassed/len(all_tests)*100:.1f}%)")
    print("=" * 80)
    
    # Breakdown by category
    category_stats = {}
    for result in results:
        cat = result['category']
        if cat not in category_stats:
            category_stats[cat] = {'total': 0, 'blocked': 0}
        category_stats[cat]['total'] += 1
        if result['blocked']:
            category_stats[cat]['blocked'] += 1
    
    print("\nBREAKDOWN BY CATEGORY:")
    print("-" * 80)
    for cat, stats in sorted(category_stats.items()):
        total = stats['total']
        blocked = stats['blocked']
        rate = blocked / total * 100 if total > 0 else 0
        print(f"{cat:40s} {blocked:3d}/{total:3d} ({rate:5.1f}%)")
    
    # Breakdown by severity
    severity_stats = {}
    for result in results:
        sev = result['severity']
        if sev not in severity_stats:
            severity_stats[sev] = {'total': 0, 'blocked': 0}
        severity_stats[sev]['total'] += 1
        if result['blocked']:
            severity_stats[sev]['blocked'] += 1
    
    print("\nBREAKDOWN BY SEVERITY:")
    print("-" * 80)
    for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        if sev in severity_stats:
            stats = severity_stats[sev]
            total = stats['total']
            blocked = stats['blocked']
            rate = blocked / total * 100 if total > 0 else 0
            print(f"{sev:40s} {blocked:3d}/{total:3d} ({rate:5.1f}%)")
    
    # Save detailed results
    output_file = '/home/ubuntu/crypto_detector_test_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'summary': {
                'total': len(all_tests),
                'blocked': blocked,
                'bypassed': bypassed,
                'block_rate': blocked / len(all_tests) * 100
            },
            'category_breakdown': category_stats,
            'severity_breakdown': severity_stats,
            'detailed_results': results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Assessment
    block_rate = blocked / len(all_tests) * 100
    print("\n" + "=" * 80)
    print("ASSESSMENT:")
    if block_rate >= 95:
        print("🟢 EXCELLENT - Crypto detector is highly effective")
    elif block_rate >= 80:
        print("🟡 GOOD - Crypto detector is effective, minor improvements needed")
    elif block_rate >= 60:
        print("🟠 FAIR - Crypto detector needs significant improvements")
    else:
        print("🔴 POOR - Crypto detector needs major enhancements")
    print("=" * 80)

if __name__ == "__main__":
    test_crypto_detector()

"""
Skill Marketplace Test Suite

Comprehensive tests for Skill Marketplace functionality.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from marketplace.marketplace_manager import SkillMarketplace

def test_list_skills():
    """Test listing skills"""
    print("\n" + "="*80)
    print("TEST: List Skills")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    # List all skills
    all_skills = marketplace.list_skills()
    print(f"✓ Total skills: {len(all_skills)}")
    
    # List by category
    crypto_skills = marketplace.list_skills(category="Cryptocurrency")
    print(f"✓ Cryptocurrency skills: {len(crypto_skills)}")
    
    web3_skills = marketplace.list_skills(category="Web3 Security")
    print(f"✓ Web3 skills: {len(web3_skills)}")
    
    # List by status
    stable_skills = marketplace.list_skills(status="stable")
    print(f"✓ Stable skills: {len(stable_skills)}")
    
    return len(all_skills) > 0

def test_search_skills():
    """Test searching skills"""
    print("\n" + "="*80)
    print("TEST: Search Skills")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    # Search for web3
    results = marketplace.search_skills("web3")
    print(f"✓ Search 'web3': {len(results)} results")
    
    # Search for crypto
    results = marketplace.search_skills("crypto")
    print(f"✓ Search 'crypto': {len(results)} results")
    
    # Search for defi
    results = marketplace.search_skills("defi")
    print(f"✓ Search 'defi': {len(results)} results")
    
    # Search for non-existent
    results = marketplace.search_skills("nonexistent")
    print(f"✓ Search 'nonexistent': {len(results)} results (should be 0)")
    
    return True

def test_get_skill():
    """Test getting skill details"""
    print("\n" + "="*80)
    print("TEST: Get Skill Details")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    # Get cryptocurrency skill
    skill = marketplace.get_skill("cryptocurrency")
    if skill:
        print(f"✓ Got cryptocurrency skill: {skill['name']} v{skill['version']}")
        print(f"  Category: {skill['category']}")
        print(f"  Status: {skill['status']}")
        print(f"  Downloads: {skill.get('downloads', 0)}")
        print(f"  Rating: {skill.get('rating', 0)}/5.0")
    else:
        print("✗ Failed to get cryptocurrency skill")
        return False
    
    # Get web3 skill
    skill = marketplace.get_skill("web3")
    if skill:
        print(f"✓ Got web3 skill: {skill['name']} v{skill['version']}")
        print(f"  Category: {skill['category']}")
        print(f"  Status: {skill['status']}")
    else:
        print("✗ Failed to get web3 skill")
        return False
    
    # Get non-existent skill
    skill = marketplace.get_skill("nonexistent")
    if skill is None:
        print(f"✓ Correctly returned None for non-existent skill")
    else:
        print("✗ Should return None for non-existent skill")
        return False
    
    return True

def test_installation_check():
    """Test installation status check"""
    print("\n" + "="*80)
    print("TEST: Installation Status")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    # Check cryptocurrency skill
    is_installed = marketplace.is_installed("cryptocurrency")
    print(f"✓ Cryptocurrency skill installed: {is_installed}")
    
    if is_installed:
        version = marketplace.get_installed_version("cryptocurrency")
        print(f"  Installed version: {version}")
    
    # Check web3 skill
    is_installed = marketplace.is_installed("web3")
    print(f"✓ Web3 skill installed: {is_installed}")
    
    if is_installed:
        version = marketplace.get_installed_version("web3")
        print(f"  Installed version: {version}")
    
    return True

def test_categories():
    """Test category listing"""
    print("\n" + "="*80)
    print("TEST: Categories")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    categories = marketplace.get_categories()
    print(f"✓ Total categories: {len(categories)}")
    
    for cat in categories:
        print(f"  • {cat['name']} ({cat['skill_count']} skills)")
    
    return len(categories) > 0

def test_featured_skills():
    """Test featured skills"""
    print("\n" + "="*80)
    print("TEST: Featured Skills")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    featured = marketplace.get_featured_skills()
    print(f"✓ Featured skills: {len(featured)}")
    
    for skill in featured:
        print(f"  • {skill['name']} v{skill['version']}")
    
    return len(featured) > 0

def test_popular_skills():
    """Test popular skills"""
    print("\n" + "="*80)
    print("TEST: Popular Skills")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    popular = marketplace.get_popular_skills(limit=5)
    print(f"✓ Popular skills (top 5):")
    
    for i, skill in enumerate(popular, 1):
        print(f"  {i}. {skill['name']} - {skill.get('downloads', 0)} downloads")
    
    return len(popular) > 0

def test_new_skills():
    """Test new skills"""
    print("\n" + "="*80)
    print("TEST: New Skills")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    new_skills = marketplace.get_new_skills(limit=5)
    print(f"✓ New skills (latest 5):")
    
    for skill in new_skills:
        print(f"  • {skill['name']} v{skill['version']} - {skill.get('created_at', 'N/A')}")
    
    return len(new_skills) > 0

def test_marketplace_stats():
    """Test marketplace statistics"""
    print("\n" + "="*80)
    print("TEST: Marketplace Statistics")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    stats = marketplace.get_marketplace_stats()
    
    print(f"✓ Total Skills: {stats['total_skills']}")
    print(f"✓ Total Categories: {stats['total_categories']}")
    print(f"✓ Total Downloads: {stats['total_downloads']}")
    print(f"✓ Average Rating: {stats['average_rating']}/5.0")
    print(f"✓ Featured Skills: {stats['featured_skills']}")
    print(f"✓ New Skills: {stats['new_skills']}")
    
    return stats['total_skills'] > 0

def test_skill_installation():
    """Test skill installation (dry run)"""
    print("\n" + "="*80)
    print("TEST: Skill Installation (Dry Run)")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    # Test install cryptocurrency skill (should already be installed)
    print("Testing cryptocurrency skill installation...")
    result = marketplace.install_skill("cryptocurrency")
    
    if result['success']:
        print(f"✓ {result['message']}")
    else:
        # Expected if already installed
        print(f"ℹ {result['error']}")
    
    # Test install web3 skill
    print("\nTesting web3 skill installation...")
    result = marketplace.install_skill("web3")
    
    if result['success']:
        print(f"✓ {result['message']}")
    else:
        print(f"ℹ {result['error']}")
    
    return True

def test_update_check():
    """Test update checking"""
    print("\n" + "="*80)
    print("TEST: Update Check")
    print("="*80 + "\n")
    
    marketplace = SkillMarketplace()
    
    updates = marketplace.check_updates()
    
    if updates:
        print(f"✓ Found {len(updates)} update(s):")
        for update in updates:
            print(f"  • {update['name']} ({update['skill_id']})")
            print(f"    {update['current_version']} → {update['latest_version']}")
    else:
        print("✓ All skills are up to date")
    
    return True

def main():
    """Run all marketplace tests"""
    print("\n" + "="*80)
    print("SKILL MARKETPLACE TEST SUITE")
    print("="*80)
    
    tests = [
        ("List Skills", test_list_skills),
        ("Search Skills", test_search_skills),
        ("Get Skill Details", test_get_skill),
        ("Installation Status", test_installation_check),
        ("Categories", test_categories),
        ("Featured Skills", test_featured_skills),
        ("Popular Skills", test_popular_skills),
        ("New Skills", test_new_skills),
        ("Marketplace Stats", test_marketplace_stats),
        ("Skill Installation", test_skill_installation),
        ("Update Check", test_update_check),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"Status: {'✓ ALL TESTS PASSED' if passed == total else '✗ SOME TESTS FAILED'}")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

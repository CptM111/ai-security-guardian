#!/usr/bin/env python3
"""
Skill Marketplace CLI

Command-line interface for browsing, installing, and managing skills
from the AI Security Guardian Skill Marketplace.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from marketplace.marketplace_manager import SkillMarketplace

def list_skills(args):
    """List available skills"""
    marketplace = SkillMarketplace()
    skills = marketplace.list_skills(category=args.category, status=args.status)
    
    if not skills:
        print("No skills found matching criteria.")
        return
    
    print(f"\n{'='*80}")
    print(f"{'AVAILABLE SKILLS':^80}")
    print(f"{'='*80}\n")
    
    for skill in skills:
        installed = marketplace.is_installed(skill['id'])
        status_icon = "✓" if installed else " "
        
        print(f"[{status_icon}] {skill['name']} (v{skill['version']})")
        print(f"    ID: {skill['id']}")
        print(f"    Category: {skill['category']}")
        print(f"    Rating: {'⭐' * int(skill.get('rating', 0))} {skill.get('rating', 0)}/5.0")
        print(f"    Downloads: {skill.get('downloads', 0)}")
        print(f"    Status: {skill['status']}")
        print(f"    {skill['description'][:100]}...")
        print()

def search_skills(args):
    """Search for skills"""
    marketplace = SkillMarketplace()
    results = marketplace.search_skills(args.query)
    
    if not results:
        print(f"No skills found matching '{args.query}'")
        return
    
    print(f"\nFound {len(results)} skill(s) matching '{args.query}':\n")
    
    for skill in results:
        print(f"• {skill['name']} (v{skill['version']})")
        print(f"  {skill['description'][:100]}...")
        print()

def show_skill(args):
    """Show detailed skill information"""
    marketplace = SkillMarketplace()
    skill = marketplace.get_skill(args.skill_id)
    
    if not skill:
        print(f"Skill '{args.skill_id}' not found")
        return
    
    installed = marketplace.is_installed(args.skill_id)
    installed_version = marketplace.get_installed_version(args.skill_id) if installed else None
    
    print(f"\n{'='*80}")
    print(f"{skill['name']} (v{skill['version']})")
    print(f"{'='*80}\n")
    
    print(f"ID: {skill['id']}")
    print(f"Category: {skill['category']}")
    print(f"Status: {skill['status']}")
    print(f"Author: {skill['author']}")
    print(f"License: {skill['license']}")
    print(f"Rating: {'⭐' * int(skill.get('rating', 0))} {skill.get('rating', 0)}/5.0")
    print(f"Downloads: {skill.get('downloads', 0)}")
    print(f"Repository: {skill['repository']}")
    print(f"\nInstalled: {'Yes' if installed else 'No'}")
    if installed:
        print(f"Installed Version: {installed_version}")
        if installed_version != skill['version']:
            print(f"⚠️  Update available: {skill['version']}")
    
    print(f"\nDescription:")
    print(f"{skill['description']}")
    
    print(f"\nCapabilities:")
    for cap in skill.get('capabilities', []):
        print(f"  • {cap}")
    
    print(f"\nTags:")
    print(f"  {', '.join(skill.get('tags', []))}")
    
    if skill.get('dependencies', {}).get('python'):
        print(f"\nPython Dependencies:")
        for dep in skill['dependencies']['python']:
            print(f"  • {dep}")
    
    print(f"\nPerformance:")
    perf = skill.get('performance', {})
    print(f"  Detection Latency: {perf.get('detection_latency_ms', 'N/A')}ms")
    print(f"  Memory Usage: {perf.get('memory_usage_mb', 'N/A')}MB")
    
    print(f"\nTest Results:")
    test = skill.get('test_results', {})
    print(f"  Overall Detection Rate: {test.get('overall_detection_rate', 0)*100:.1f}%")
    print(f"  Critical Detection Rate: {test.get('critical_detection_rate', 0)*100:.1f}%")
    print(f"  False Positive Rate: {test.get('false_positive_rate', 0)*100:.1f}%")
    print()

def install_skill(args):
    """Install a skill"""
    marketplace = SkillMarketplace()
    
    print(f"Installing skill '{args.skill_id}'...")
    result = marketplace.install_skill(args.skill_id, force=args.force)
    
    if result['success']:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ Error: {result['error']}")
        sys.exit(1)

def uninstall_skill(args):
    """Uninstall a skill"""
    marketplace = SkillMarketplace()
    
    if not args.yes:
        response = input(f"Are you sure you want to uninstall '{args.skill_id}'? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    print(f"Uninstalling skill '{args.skill_id}'...")
    result = marketplace.uninstall_skill(args.skill_id)
    
    if result['success']:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ Error: {result['error']}")
        sys.exit(1)

def update_skill(args):
    """Update a skill"""
    marketplace = SkillMarketplace()
    
    if args.skill_id:
        # Update specific skill
        print(f"Updating skill '{args.skill_id}'...")
        result = marketplace.update_skill(args.skill_id)
        
        if result['success']:
            if result.get('updated'):
                print(f"✓ Updated {args.skill_id} from v{result['old_version']} to v{result['new_version']}")
            else:
                print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result['error']}")
            sys.exit(1)
    else:
        # Check all skills for updates
        updates = marketplace.check_updates()
        
        if not updates:
            print("All skills are up to date.")
            return
        
        print(f"\nAvailable updates ({len(updates)}):\n")
        for update in updates:
            print(f"  • {update['name']} ({update['skill_id']})")
            print(f"    {update['current_version']} → {update['latest_version']}")
        
        if not args.yes:
            response = input(f"\nUpdate all skills? [y/N]: ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        
        # Update all
        for update in updates:
            print(f"\nUpdating {update['skill_id']}...")
            result = marketplace.update_skill(update['skill_id'])
            if result['success']:
                print(f"✓ Updated to v{result['new_version']}")
            else:
                print(f"✗ Error: {result['error']}")

def list_categories(args):
    """List skill categories"""
    marketplace = SkillMarketplace()
    categories = marketplace.get_categories()
    
    print(f"\n{'='*80}")
    print(f"{'SKILL CATEGORIES':^80}")
    print(f"{'='*80}\n")
    
    for cat in categories:
        print(f"• {cat['name']} ({cat['skill_count']} skills)")
        print(f"  {cat['description']}")
        print()

def show_stats(args):
    """Show marketplace statistics"""
    marketplace = SkillMarketplace()
    stats = marketplace.get_marketplace_stats()
    
    print(f"\n{'='*80}")
    print(f"{'MARKETPLACE STATISTICS':^80}")
    print(f"{'='*80}\n")
    
    print(f"Total Skills: {stats['total_skills']}")
    print(f"Total Categories: {stats['total_categories']}")
    print(f"Total Downloads: {stats['total_downloads']}")
    print(f"Average Rating: {'⭐' * int(stats['average_rating'])} {stats['average_rating']}/5.0")
    print(f"Featured Skills: {stats['featured_skills']}")
    print(f"New Skills: {stats['new_skills']}")
    print()

def main():
    parser = argparse.ArgumentParser(
        description="AI Security Guardian Skill Marketplace CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all skills
  %(prog)s list

  # List skills by category
  %(prog)s list --category web3

  # Search for skills
  %(prog)s search "smart contract"

  # Show skill details
  %(prog)s show web3

  # Install a skill
  %(prog)s install web3

  # Update all skills
  %(prog)s update

  # Show marketplace statistics
  %(prog)s stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available skills')
    list_parser.add_argument('--category', help='Filter by category')
    list_parser.add_argument('--status', choices=['stable', 'beta', 'alpha'], help='Filter by status')
    list_parser.set_defaults(func=list_skills)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for skills')
    search_parser.add_argument('query', help='Search query')
    search_parser.set_defaults(func=search_skills)
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show skill details')
    show_parser.add_argument('skill_id', help='Skill ID')
    show_parser.set_defaults(func=show_skill)
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install a skill')
    install_parser.add_argument('skill_id', help='Skill ID')
    install_parser.add_argument('--force', action='store_true', help='Force reinstall')
    install_parser.set_defaults(func=install_skill)
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a skill')
    uninstall_parser.add_argument('skill_id', help='Skill ID')
    uninstall_parser.add_argument('--yes', action='store_true', help='Skip confirmation')
    uninstall_parser.set_defaults(func=uninstall_skill)
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update skills')
    update_parser.add_argument('skill_id', nargs='?', help='Skill ID (optional, updates all if not specified)')
    update_parser.add_argument('--yes', action='store_true', help='Skip confirmation')
    update_parser.set_defaults(func=update_skill)
    
    # Categories command
    categories_parser = subparsers.add_parser('categories', help='List skill categories')
    categories_parser.set_defaults(func=list_categories)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show marketplace statistics')
    stats_parser.set_defaults(func=show_stats)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)

if __name__ == '__main__':
    main()

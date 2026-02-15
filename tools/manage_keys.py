#!/usr/bin/env python3
"""
API Key Management CLI Tool

Usage:
    python manage_keys.py generate --name "My App" --expires 30
    python manage_keys.py list
    python manage_keys.py revoke --key-id key_abc123
    python manage_keys.py stats
"""

import sys
import os
import argparse
from pathlib import Path
from tabulate import tabulate

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth.api_key_manager import APIKeyManager


def generate_key(args):
    """Generate a new API key"""
    manager = APIKeyManager(args.db_path)
    
    raw_key, api_key = manager.generate_key(
        name=args.name,
        expires_in_days=args.expires,
        rate_limit=args.rate_limit
    )
    
    print("=" * 80)
    print("✅ API KEY GENERATED SUCCESSFULLY")
    print("=" * 80)
    print()
    print(f"🔑 API Key:  {raw_key}")
    print()
    print("⚠️  IMPORTANT: Save this key securely! It cannot be retrieved later.")
    print()
    print("Key Details:")
    print(f"  - Key ID:      {api_key.key_id}")
    print(f"  - Name:        {api_key.name}")
    print(f"  - Created:     {api_key.created_at}")
    print(f"  - Expires:     {api_key.expires_at or 'Never'}")
    print(f"  - Rate Limit:  {api_key.rate_limit} requests/minute")
    print()
    print("Usage Example:")
    print(f'  curl -H "Authorization: Bearer {raw_key}" \\')
    print(f'       http://localhost:8000/api/v1/protect/prompt')
    print()
    print("=" * 80)


def list_keys(args):
    """List all API keys"""
    manager = APIKeyManager(args.db_path)
    keys = manager.list_keys(include_inactive=args.all)
    
    if not keys:
        print("No API keys found.")
        return
    
    # Prepare table data
    table_data = []
    for key in keys:
        status = "✅ Active" if key.is_active else "❌ Revoked"
        expires = key.expires_at[:10] if key.expires_at else "Never"
        last_used = key.last_used_at[:10] if key.last_used_at else "Never"
        
        table_data.append([
            key.key_id,
            key.name,
            status,
            key.created_at[:10],
            expires,
            last_used,
            key.usage_count,
            key.rate_limit
        ])
    
    headers = ["Key ID", "Name", "Status", "Created", "Expires", "Last Used", "Usage", "Rate Limit"]
    
    print()
    print(f"Total Keys: {len(keys)}")
    print()
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print()


def revoke_key(args):
    """Revoke an API key"""
    manager = APIKeyManager(args.db_path)
    
    # Get key info first
    key_info = manager.get_key_info(args.key_id)
    if not key_info:
        print(f"❌ Error: Key ID '{args.key_id}' not found.")
        return
    
    if not key_info.is_active:
        print(f"⚠️  Key '{args.key_id}' is already revoked.")
        return
    
    # Confirm revocation
    if not args.yes:
        print(f"About to revoke key:")
        print(f"  - Key ID: {key_info.key_id}")
        print(f"  - Name:   {key_info.name}")
        print(f"  - Usage:  {key_info.usage_count} requests")
        print()
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            print("Revocation cancelled.")
            return
    
    # Revoke the key
    success = manager.revoke_key(args.key_id)
    
    if success:
        print(f"✅ Key '{args.key_id}' has been revoked successfully.")
    else:
        print(f"❌ Failed to revoke key '{args.key_id}'.")


def show_stats(args):
    """Show API key statistics"""
    manager = APIKeyManager(args.db_path)
    stats = manager.get_statistics()
    
    print()
    print("=" * 50)
    print("API KEY STATISTICS")
    print("=" * 50)
    print()
    print(f"  Active Keys:   {stats['active_keys']}")
    print(f"  Revoked Keys:  {stats['revoked_keys']}")
    print(f"  Total Keys:    {stats['total_keys']}")
    print(f"  Total Usage:   {stats['total_usage']} requests")
    print()
    print("=" * 50)
    print()


def show_key_info(args):
    """Show detailed information about a specific key"""
    manager = APIKeyManager(args.db_path)
    key_info = manager.get_key_info(args.key_id)
    
    if not key_info:
        print(f"❌ Error: Key ID '{args.key_id}' not found.")
        return
    
    status = "✅ Active" if key_info.is_active else "❌ Revoked"
    
    print()
    print("=" * 60)
    print(f"API KEY INFORMATION: {key_info.key_id}")
    print("=" * 60)
    print()
    print(f"  Name:          {key_info.name}")
    print(f"  Status:        {status}")
    print(f"  Created:       {key_info.created_at}")
    print(f"  Expires:       {key_info.expires_at or 'Never'}")
    print(f"  Last Used:     {key_info.last_used_at or 'Never'}")
    print(f"  Usage Count:   {key_info.usage_count} requests")
    print(f"  Rate Limit:    {key_info.rate_limit} requests/minute")
    if key_info.metadata:
        print(f"  Metadata:      {key_info.metadata}")
    print()
    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="AI Security Guardian - API Key Management Tool"
    )
    
    parser.add_argument(
        "--db-path",
        default="data/api_keys.db",
        help="Path to API keys database (default: data/api_keys.db)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a new API key")
    gen_parser.add_argument("--name", required=True, help="Descriptive name for the key")
    gen_parser.add_argument("--expires", type=int, help="Expiration in days (optional)")
    gen_parser.add_argument("--rate-limit", type=int, default=1000, help="Rate limit (requests/minute)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all API keys")
    list_parser.add_argument("--all", action="store_true", help="Include revoked keys")
    
    # Revoke command
    revoke_parser = subparsers.add_parser("revoke", help="Revoke an API key")
    revoke_parser.add_argument("--key-id", required=True, help="Key ID to revoke")
    revoke_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show API key statistics")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show detailed key information")
    info_parser.add_argument("--key-id", required=True, help="Key ID to show")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == "generate":
        generate_key(args)
    elif args.command == "list":
        list_keys(args)
    elif args.command == "revoke":
        revoke_key(args)
    elif args.command == "stats":
        show_stats(args)
    elif args.command == "info":
        show_key_info(args)


if __name__ == "__main__":
    main()

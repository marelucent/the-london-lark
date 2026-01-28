#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI tool for managing Lark Mind invite codes.

Usage:
    python manage_invites.py create [--count N]   Create invite code(s)
    python manage_invites.py list                  List all codes
    python manage_invites.py revoke CODE           Revoke a code
"""

import sys
import argparse
from datetime import datetime
from auth_models import InviteCode, init_auth_db


def create_codes(count=1):
    """Create new invite codes."""
    print(f"\nCreating {count} invite code(s)...\n")

    for _ in range(count):
        code = InviteCode.create(created_by='cli')
        print(f"  {code}")

    print(f"\nDone. Share these codes with people you trust.")


def list_codes():
    """List all invite codes with their status."""
    codes = InviteCode.get_all()

    if not codes:
        print("\nNo invite codes found. Create some with: python manage_invites.py create")
        return

    print(f"\n{'CODE':<14} {'STATUS':<12} {'CREATED':<20} {'USED BY':<30}")
    print("-" * 80)

    for code in codes:
        status = "USED" if code['used_by'] else ("REVOKED" if not code['is_active'] else "AVAILABLE")

        created = code['created_at'][:16] if code['created_at'] else '-'
        used_by = code['used_by_email'] or '-'

        # Color coding for terminal
        if status == "AVAILABLE":
            status_display = f"\033[92m{status}\033[0m"  # Green
        elif status == "USED":
            status_display = f"\033[90m{status}\033[0m"  # Gray
        else:
            status_display = f"\033[91m{status}\033[0m"  # Red

        print(f"  {code['code']:<12} {status_display:<21} {created:<20} {used_by:<30}")

    # Summary
    available = sum(1 for c in codes if c['is_active'] and not c['used_by'])
    used = sum(1 for c in codes if c['used_by'])
    revoked = sum(1 for c in codes if not c['is_active'] and not c['used_by'])

    print(f"\nTotal: {len(codes)} | Available: {available} | Used: {used} | Revoked: {revoked}")


def revoke_code(code):
    """Revoke an invite code."""
    if InviteCode.revoke(code):
        print(f"\nRevoked: {code.upper()}")
    else:
        print(f"\nCode not found: {code}")


def main():
    parser = argparse.ArgumentParser(
        description='Manage Lark Mind invite codes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_invites.py create           Create 1 invite code
  python manage_invites.py create --count 5 Create 5 invite codes
  python manage_invites.py list             List all codes and their status
  python manage_invites.py revoke ABC123    Revoke a specific code
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create new invite code(s)')
    create_parser.add_argument('--count', '-n', type=int, default=1,
                               help='Number of codes to create (default: 1)')

    # List command
    subparsers.add_parser('list', help='List all invite codes')

    # Revoke command
    revoke_parser = subparsers.add_parser('revoke', help='Revoke an invite code')
    revoke_parser.add_argument('code', help='The code to revoke')

    args = parser.parse_args()

    # Initialize database
    init_auth_db()

    if args.command == 'create':
        create_codes(args.count)
    elif args.command == 'list':
        list_codes()
    elif args.command == 'revoke':
        revoke_code(args.code)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

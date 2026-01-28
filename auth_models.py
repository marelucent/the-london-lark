#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication models for The London Lark.
Handles users and invite codes with SQLite storage.
"""

import sqlite3
import secrets
import string
from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

# Will be initialized by app
bcrypt = Bcrypt()

DATABASE_PATH = 'lark_auth.db'


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db():
    """Initialize the authentication database tables."""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            invite_code_used TEXT NOT NULL,
            FOREIGN KEY (invite_code_used) REFERENCES invite_codes(code)
        )
    ''')

    # Invite codes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invite_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used_by INTEGER,
            used_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (used_by) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()


class User(UserMixin):
    """User model for Flask-Login."""

    def __init__(self, id, email, password_hash, display_name, created_at, invite_code_used):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.display_name = display_name
        self.created_at = created_at
        self.invite_code_used = invite_code_used

    @staticmethod
    def get_by_id(user_id):
        """Load user by ID."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row['id'],
                email=row['email'],
                password_hash=row['password_hash'],
                display_name=row['display_name'],
                created_at=row['created_at'],
                invite_code_used=row['invite_code_used']
            )
        return None

    @staticmethod
    def get_by_email(email):
        """Load user by email."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower(),))
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(
                id=row['id'],
                email=row['email'],
                password_hash=row['password_hash'],
                display_name=row['display_name'],
                created_at=row['created_at'],
                invite_code_used=row['invite_code_used']
            )
        return None

    @staticmethod
    def create(email, password, display_name, invite_code):
        """Create a new user. Only marks invite code as used on full success."""
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db()
        cursor = conn.cursor()

        try:
            # Start transaction explicitly
            cursor.execute('BEGIN TRANSACTION')

            # Create user first
            cursor.execute('''
                INSERT INTO users (email, password_hash, display_name, invite_code_used)
                VALUES (?, ?, ?, ?)
            ''', (email.lower(), password_hash, display_name, invite_code.upper()))

            user_id = cursor.lastrowid

            # Only mark invite code as used AFTER user is successfully created
            cursor.execute('''
                UPDATE invite_codes
                SET used_by = ?, used_at = CURRENT_TIMESTAMP, is_active = 0
                WHERE code = ?
            ''', (user_id, invite_code.upper()))

            # Commit only if both operations succeeded
            conn.commit()
            conn.close()

            return User.get_by_id(user_id)

        except Exception:
            # Rollback on ANY error - invite code stays available
            conn.rollback()
            conn.close()
            return None

    def check_password(self, password):
        """Verify password."""
        return bcrypt.check_password_hash(self.password_hash, password)


class InviteCode:
    """Invite code model."""

    def __init__(self, id, code, created_by, created_at, used_by, used_at, is_active):
        self.id = id
        self.code = code
        self.created_by = created_by
        self.created_at = created_at
        self.used_by = used_by
        self.used_at = used_at
        self.is_active = is_active

    @staticmethod
    def generate_code(length=12):
        """Generate a random invite code."""
        # Use uppercase letters and digits, avoiding ambiguous characters
        alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def create(created_by='system'):
        """Create a new invite code."""
        code = InviteCode.generate_code()

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO invite_codes (code, created_by)
            VALUES (?, ?)
        ''', (code, created_by))

        conn.commit()
        conn.close()

        return code

    @staticmethod
    def validate(code):
        """Check if an invite code is valid and unused."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM invite_codes
            WHERE code = ? AND is_active = 1 AND used_by IS NULL
        ''', (code.upper(),))
        row = cursor.fetchone()
        conn.close()

        return row is not None

    @staticmethod
    def get_all():
        """Get all invite codes."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ic.*, u.email as used_by_email
            FROM invite_codes ic
            LEFT JOIN users u ON ic.used_by = u.id
            ORDER BY ic.created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def revoke(code):
        """Revoke an invite code."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE invite_codes SET is_active = 0 WHERE code = ?
        ''', (code.upper(),))
        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0

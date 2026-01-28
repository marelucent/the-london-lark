#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication models for The London Lark.
Supports PostgreSQL (production) with SQLite fallback (local dev).
"""

import os
import secrets
from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

# Will be initialized by app
bcrypt = Bcrypt()

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
USE_POSTGRES = DATABASE_URL is not None

# SQLite fallback path for local development
SQLITE_PATH = 'lark_auth.db'


def get_db():
    """Get database connection. Uses PostgreSQL if DATABASE_URL is set, else SQLite."""
    if USE_POSTGRES:
        import psycopg
        from psycopg.rows import dict_row
        # Render uses postgres:// but psycopg needs postgresql://
        db_url = DATABASE_URL
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg.connect(db_url, row_factory=dict_row)
        return conn
    else:
        import sqlite3
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn


def _param(index=None):
    """Return the correct parameter placeholder for the database."""
    return '%s' if USE_POSTGRES else '?'


def init_auth_db():
    """Initialize the authentication database tables."""
    conn = get_db()
    cursor = conn.cursor()

    if USE_POSTGRES:
        # PostgreSQL schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                invite_code_used TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invite_codes (
                id SERIAL PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_by INTEGER REFERENCES users(id),
                used_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
    else:
        # SQLite schema
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
    def _row_to_user(row):
        """Convert a database row to a User object."""
        if not row:
            return None
        # Handle both dict (PostgreSQL) and sqlite3.Row
        if hasattr(row, 'keys'):
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
    def get_by_id(user_id):
        """Load user by ID."""
        conn = get_db()
        cursor = conn.cursor()
        p = _param()
        cursor.execute(f'SELECT * FROM users WHERE id = {p}', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return User._row_to_user(row)

    @staticmethod
    def get_by_email(email):
        """Load user by email."""
        conn = get_db()
        cursor = conn.cursor()
        p = _param()
        cursor.execute(f'SELECT * FROM users WHERE email = {p}', (email.lower(),))
        row = cursor.fetchone()
        conn.close()
        return User._row_to_user(row)

    @staticmethod
    def create(email, password, display_name, invite_code):
        """Create a new user. Only marks invite code as used on full success."""
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        p = _param()

        conn = get_db()
        cursor = conn.cursor()

        try:
            if USE_POSTGRES:
                # PostgreSQL: use RETURNING to get the new ID
                cursor.execute(f'''
                    INSERT INTO users (email, password_hash, display_name, invite_code_used)
                    VALUES ({p}, {p}, {p}, {p})
                    RETURNING id
                ''', (email.lower(), password_hash, display_name, invite_code.upper()))
                user_id = cursor.fetchone()['id']
            else:
                # SQLite: use lastrowid
                cursor.execute(f'''
                    INSERT INTO users (email, password_hash, display_name, invite_code_used)
                    VALUES ({p}, {p}, {p}, {p})
                ''', (email.lower(), password_hash, display_name, invite_code.upper()))
                user_id = cursor.lastrowid

            # Mark invite code as used
            cursor.execute(f'''
                UPDATE invite_codes
                SET used_by = {p}, used_at = CURRENT_TIMESTAMP, is_active = {'FALSE' if USE_POSTGRES else '0'}
                WHERE code = {p}
            ''', (user_id, invite_code.upper()))

            conn.commit()
            conn.close()
            return User.get_by_id(user_id)

        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"User creation error: {e}")  # Log for debugging
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
        alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def create(created_by='system'):
        """Create a new invite code."""
        code = InviteCode.generate_code()
        p = _param()

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT INTO invite_codes (code, created_by)
            VALUES ({p}, {p})
        ''', (code, created_by))
        conn.commit()
        conn.close()

        return code

    @staticmethod
    def validate(code):
        """Check if an invite code is valid and unused."""
        p = _param()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT * FROM invite_codes
            WHERE code = {p} AND is_active = {'TRUE' if USE_POSTGRES else '1'} AND used_by IS NULL
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

        # Convert rows to dicts
        result = []
        for row in rows:
            if USE_POSTGRES:
                result.append(dict(row))
            else:
                result.append(dict(row))
        return result

    @staticmethod
    def revoke(code):
        """Revoke an invite code."""
        p = _param()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE invite_codes SET is_active = {'FALSE' if USE_POSTGRES else '0'} WHERE code = {p}
        ''', (code.upper(),))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

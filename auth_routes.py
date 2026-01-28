#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication routes for The London Lark.
Login, register, logout, and protected mind route.
"""

import os
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from auth_models import User, InviteCode
from lark_mind import get_time_aware_greeting as get_lark_mind_greeting

auth_bp = Blueprint('auth', __name__)

# Admin password - set via environment variable, fallback for dev
ADMIN_PASSWORD = os.environ.get('LARK_ADMIN_PASSWORD', 'lark-admin-dev')


def admin_required(f):
    """Decorator to require admin authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('auth.admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('auth.mind'))

    error = None

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            error = "Both fields are required, petal."
        else:
            user = User.get_by_email(email)
            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('auth.mind'))
            else:
                error = "The Lark doesn't recognise those words."

    return render_template('login.html', error=error)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('auth.mind'))

    error = None

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        display_name = request.form.get('display_name', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        invite_code = request.form.get('invite_code', '').strip()

        # Validation
        if not all([email, display_name, password, invite_code]):
            error = "All fields are required, petal."
        elif password != password_confirm:
            error = "Your passwords don't match."
        elif len(password) < 8:
            error = "Choose a password of at least 8 characters."
        elif not InviteCode.validate(invite_code):
            error = "That invitation isn't recognised. Perhaps it's already been used?"
        elif User.get_by_email(email):
            error = "Someone with that email already knows the Lark."
        else:
            # Create user
            user = User.create(
                email=email,
                password=password,
                display_name=display_name,
                invite_code=invite_code.upper()
            )

            if user:
                login_user(user)
                return redirect(url_for('auth.mind'))
            else:
                error = "Something went awry. Try again?"

    return render_template('register.html', error=error)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout and redirect to home."""
    logout_user()
    return redirect(url_for('home'))


@auth_bp.route('/mind')
def mind():
    """
    Lark Mind - protected conversational AI.
    Shows locked page for anonymous users, full interface for authenticated.
    """
    if not current_user.is_authenticated:
        return render_template('mind_locked.html')

    greeting = get_lark_mind_greeting()
    return render_template('mind.html', greeting=greeting, user=current_user)


# =============================================================================
# ADMIN ROUTES
# =============================================================================

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    error = None

    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            next_url = request.args.get('next', url_for('auth.admin_invites'))
            return redirect(next_url)
        else:
            error = "Incorrect password"

    return render_template('admin_login.html', error=error)


@auth_bp.route('/admin/logout')
def admin_logout():
    """Admin logout."""
    session.pop('admin_authenticated', None)
    return redirect(url_for('home'))


@auth_bp.route('/admin/invites')
@admin_required
def admin_invites():
    """View all invite codes."""
    codes = InviteCode.get_all()
    new_codes = session.pop('new_codes', None)
    return render_template('admin_invites.html', codes=codes, new_codes=new_codes)


@auth_bp.route('/admin/invites/create', methods=['POST'])
@admin_required
def admin_invites_create():
    """Generate new invite codes."""
    count = int(request.form.get('count', 1))
    count = min(max(count, 1), 10)  # Clamp between 1-10

    new_codes = []
    for _ in range(count):
        code = InviteCode.create(created_by='admin')
        new_codes.append(code)

    session['new_codes'] = new_codes
    return redirect(url_for('auth.admin_invites'))


@auth_bp.route('/admin/invites/revoke/<code>', methods=['POST'])
@admin_required
def admin_invites_revoke(code):
    """Revoke an invite code."""
    InviteCode.revoke(code)
    return redirect(url_for('auth.admin_invites'))

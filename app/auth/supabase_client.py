"""Supabase client initialization."""

from flask import current_app, g
from supabase import Client, create_client


def get_supabase_client() -> Client:
    """Get or create Supabase client for the current request."""
    if "supabase" not in g:
        g.supabase = create_client(
            current_app.config["SUPABASE_URL"], current_app.config["SUPABASE_ANON_KEY"]
        )
    return g.supabase


def get_supabase_admin_client() -> Client:
    """Get Supabase client with service role (admin) privileges."""
    if "supabase_admin" not in g:
        g.supabase_admin = create_client(
            current_app.config["SUPABASE_URL"],
            current_app.config["SUPABASE_SERVICE_ROLE_KEY"],
        )
    return g.supabase_admin

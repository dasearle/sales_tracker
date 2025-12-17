"""Authentication routes."""

from flask import redirect, url_for, session, request, current_app, render_template
from app.auth import bp
from app.auth.supabase_client import get_supabase_client


@bp.route("/login")
def login():
    """Initiate Microsoft 365 SSO login via Supabase."""
    supabase = get_supabase_client()
    redirect_url = f"{current_app.config['REDIRECT_BASE_URL']}/auth/callback"

    response = supabase.auth.sign_in_with_oauth(
        {
            "provider": "azure",
            "options": {"redirect_to": redirect_url, "scopes": "email profile openid"},
        }
    )

    return redirect(response.url)


@bp.route("/callback")
def callback():
    """Handle OAuth callback from Supabase."""
    access_token = request.args.get("access_token")
    refresh_token = request.args.get("refresh_token")

    if access_token:
        # Store tokens in session
        session["access_token"] = access_token
        session["refresh_token"] = refresh_token

        # Get user info
        supabase = get_supabase_client()
        supabase.auth.set_session(access_token, refresh_token)
        user_response = supabase.auth.get_user()

        if user_response and user_response.user:
            user = user_response.user
            session["user"] = {
                "id": user.id,
                "email": user.email,
                "role": user.app_metadata.get("role", "sales")
                if user.app_metadata
                else "sales",
            }

        return redirect(url_for("main.dashboard"))

    # If no token in URL, render a page that extracts from hash fragment
    return render_template("auth/callback.html")


@bp.route("/logout")
def logout():
    """Log out the current user."""
    supabase = get_supabase_client()

    if "access_token" in session:
        try:
            supabase.auth.sign_out()
        except Exception:
            pass  # Token might be expired

    session.clear()
    return redirect(url_for("main.index"))
    return redirect(url_for('main.index'))

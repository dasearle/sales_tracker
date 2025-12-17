"""Main application routes."""

from flask import render_template, session

from app.auth.decorators import require_login, require_role
from app.main import bp


@bp.route("/")
def index():
    """Home page - public."""
    return render_template("index.html")


@bp.route("/dashboard")
@require_login
def dashboard():
    """Dashboard - requires login (any role)."""
    return render_template("dashboard.html", user=session.get("user"))


@bp.route("/sales")
@require_role("sales", "admin", "management")
def sales():
    """Sales page - Sales, Admin, or Management only."""
    return render_template("sales.html", user=session.get("user"))


@bp.route("/marketing")
@require_role("marketing", "admin", "management")
def marketing():
    """Marketing page - Marketing, Admin, or Management only."""
    return render_template("marketing.html", user=session.get("user"))


@bp.route("/reports")
@require_role("admin", "management")
def reports():
    """Reports page - Admin or Management only."""
    return render_template("reports.html", user=session.get("user"))


@bp.errorhandler(403)
def forbidden(e):
    """Handle 403 Forbidden errors."""
    return render_template("403.html"), 403

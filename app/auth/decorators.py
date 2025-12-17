"""Authentication decorators."""

from functools import wraps

from flask import abort, flash, redirect, session, url_for


def require_login(f):
    """Decorator to require user to be logged in."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def require_role(*allowed_roles):
    """
    Decorator to require user to have one of the specified roles.

    Usage:
        @require_role('admin')
        @require_role('admin', 'management')
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in session:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for("auth.login"))

            user_role = session["user"].get("role", "sales")

            if user_role not in allowed_roles:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_admin(f):
    """Decorator to require admin role."""
    return require_role("admin")(f)


def require_management_or_admin(f):
    """Decorator to require management or admin role."""
    return require_role("admin", "management")(f)

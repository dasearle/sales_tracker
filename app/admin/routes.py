"""Admin routes for role management."""

from flask import render_template, request, jsonify, session
from app.admin import bp
from app.auth.decorators import require_admin
from app.auth.supabase_client import get_supabase_admin_client


@bp.route("/users")
@require_admin
def users():
    """List all users and their roles."""
    supabase = get_supabase_admin_client()

    # Get all users with their roles
    response = (
        supabase.table("user_roles")
        .select("user_id, role, created_at, updated_at")
        .execute()
    )

    # Get user emails from auth.users (requires admin client)
    users_data = []
    for role_record in response.data:
        try:
            user_response = supabase.auth.admin.get_user_by_id(role_record["user_id"])
            if user_response and user_response.user:
                users_data.append(
                    {
                        "id": role_record["user_id"],
                        "email": user_response.user.email,
                        "role": role_record["role"],
                        "created_at": role_record["created_at"],
                    }
                )
        except Exception:
            # Skip users that can't be retrieved
            continue

    return render_template("admin/users.html", users=users_data)


@bp.route("/users/<user_id>/role", methods=["PUT"])
@require_admin
def update_user_role(user_id):
    """Update a user's role."""
    data = request.get_json()
    new_role = data.get("role")

    valid_roles = ["admin", "sales", "marketing", "management"]
    if new_role not in valid_roles:
        return jsonify({"error": "Invalid role"}), 400

    # Prevent admin from removing their own admin role
    if user_id == session["user"]["id"] and new_role != "admin":
        return jsonify({"error": "Cannot remove your own admin role"}), 400

    supabase = get_supabase_admin_client()

    response = (
        supabase.table("user_roles")
        .update({"role": new_role})
        .eq("user_id", user_id)
        .execute()
    )

    if response.data:
        return jsonify({"success": True, "role": new_role})
    else:
        return jsonify({"error": "User not found"}), 404
        return jsonify({'error': 'User not found'}), 404

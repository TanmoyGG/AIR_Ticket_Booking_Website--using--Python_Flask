from flask import Blueprint, render_template, request, redirect, url_for, session, g
import mysql.connector
import bcrypt

account_bp = Blueprint('account', __name__)

@account_bp.route("/account")
def account():
    if 'user_email' not in session:
        return redirect(url_for('login.login_page', error="Please log in to view your account."))

    conn = g.db_conn
    cursor = g.db_cursor
    user_email = session['user_email']
    # Fetch current user details
    cursor.execute("SELECT username FROM Users WHERE email = %s", (user_email,))
    user_row = cursor.fetchone()
    user_name = user_row['username'] if user_row else session.get("user_name")
    status = request.args.get("status")
    success = request.args.get("success")
    error = request.args.get("error")
    return render_template("account.html", user_email=user_email, user_name=user_name, status=status, success=success, error=error)


@account_bp.route("/delete-account", methods=['POST'])
def delete_account():
    if 'user_email' not in session:
        return redirect(url_for('login.login_page', error="Authentication required."))

    user_email = session.get("user_email")
    conn = g.db_conn
    cursor = g.db_cursor

    try:
        sql_delete_user = "DELETE FROM Users WHERE email = %s"
        cursor.execute(sql_delete_user, (user_email,))
        conn.commit()
        session.clear()
        return redirect(url_for("login.login_page", status="Account Deleted Successfully"))

    except mysql.connector.Error as err:
        conn.rollback()
        return redirect(url_for('account.account', error="Failed to delete account due to a database error."))


@account_bp.route("/update-account", methods=['POST'])
def update_account():
    if 'user_email' not in session:
        return redirect(url_for('login.login_page', error="Authentication required."))

    current_email = session['user_email']
    conn = g.db_conn
    cursor = g.db_cursor
    new_name = request.form.get("user_name")
    new_email = request.form.get("user_new_email")
    new_password = request.form.get("user_password")

    # Build update parts
    update_parts = []
    params = []

    if new_name and new_name != session.get('user_name'):
        update_parts.append("username = %s")
        params.append(new_name)

    if new_email and new_email != current_email:
        cursor.execute("SELECT user_id FROM Users WHERE email = %s", (new_email,))
        if cursor.fetchone():
            return redirect(url_for('account.account', error=f"Email {new_email} already in use."))
        update_parts.append("email = %s")
        params.append(new_email)

    if new_password:
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        update_parts.append("password_hash = %s")
        params.append(hashed)

    if not update_parts:
        return redirect(url_for('account.account', status="No changes submitted."))

    sql = f"UPDATE Users SET {', '.join(update_parts)} WHERE email = %s"
    params.append(current_email)

    try:
        cursor.execute(sql, tuple(params))
        conn.commit()

        if new_name:
            session['user_name'] = new_name
        if new_email:
            session['user_email'] = new_email

        return redirect(url_for('account.account', success="Account updated successfully."))

    except mysql.connector.Error:
        conn.rollback()
        return redirect(url_for('account.account', error="Database error updating account."))

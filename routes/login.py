
from flask import Blueprint, render_template, request, redirect, url_for, session, g
import mysql.connector
import bcrypt  # Ensure bcrypt is imported

login_bp = Blueprint('login', __name__)


@login_bp.route("/login", methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    print(f"\n--Login attempt for email : {email}\n")

    try:
        if not hasattr(g, 'db_cursor') or g.db_cursor is None:
            print("Database connection not available.")
            return render_template("login.html", error="Database connection error. Please try again later.")

        cursor = g.db_cursor

        # Fetch user details including hashed password and role
        sql_user = "SELECT user_id, username, email, password_hash, role FROM Users WHERE email = %s"
        cursor.execute(sql_user, (email,))
        user = cursor.fetchone()

        # Check password using bcrypt
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Password matches
            print(f"\n--Credentials valid for {email}\n")
            user_name = user["username"]
            user_role = user["role"]  # Get user role

            # Set session variables
            session["user_email"] = user["email"]
            session["user_name"] = user["username"]
            session["user_role"] = user_role  # Store role in session

            # Redirect based on role
            if user_role == 'admin':
                # Redirect admin user to the admin dashboard
                print("\n--Admin user logged in. Redirecting to admin dashboard.\n")
                return redirect(url_for("admin.dashboard"))  # Correct redirect
            else:
                # Redirect standard user to homepage
                return redirect(url_for("homepage.homepage"))

        else:
            # Invalid credentials or user not found
            print(f"\n--Invalid credentials or user {email} not found.\n")
            return render_template("login.html", error="Invalid Credentials")

    except mysql.connector.Error as err:
        print(f"Database error during login: {err}")
        return render_template("login.html", error="An error occurred. Please try again.")
    except Exception as e:
        print(f"Error during login: {e}")  # Catch potential bcrypt errors
        return render_template("login.html", error="An authentication error occurred.")


@login_bp.route("/logout", methods=['GET'])
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('user_role', None)  # Clear role
    session.pop('user_flights', None)  # Clear any remnants if needed
    session.pop('payment_details', None)  # Clear payment details
    print("\n--Logged out successfully\n")
    # Redirect to login page after logout
    return redirect(url_for("login.login_page", status="Logged Out Successfully"))


@login_bp.route("/login", methods=['GET'])
def login_page():
    # If user is already logged in, redirect to homepage
    if 'user_email' in session:
        return redirect(url_for('homepage.homepage'))
    status = request.args.get("status")  # Get status message from logout/delete
    error = request.args.get("error")
    return render_template("login.html", status=status, error=error)


from flask import Blueprint, render_template, request, redirect, url_for, session, g
import mysql.connector
import bcrypt

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Get cursor from Flask's g object
            if not hasattr(g, 'db_cursor') or g.db_cursor is None or not hasattr(g, 'db_conn') or g.db_conn is None:
                print("Database connection not available for signup.")
                return render_template('signup.html', error='Database connection error. Please try again later.')

            cursor = g.db_cursor
            conn = g.db_conn

            # Check if the email or username already exists in the database
            sql_check = "SELECT user_id FROM Users WHERE email = %s OR username = %s"
            cursor.execute(sql_check, (email, username))
            existing_user = cursor.fetchone()

            if existing_user:
                return render_template('signup.html', error='Email or username already exists')

            # Hash the password using bcrypt
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # Insert the new user with first_name, last_name, username, email, password_hash
            sql_insert_user = (
                "INSERT INTO Users (first_name, last_name, username, email, password_hash) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            cursor.execute(sql_insert_user, (first_name, last_name, username, email, hashed_password))

            # Commit the changes to the database
            conn.commit()

            # Store basic info in session (including default role)
            session['user_name'] = username
            session['user_email'] = email
            session['user_role'] = 'user'  # Default role

            # Redirect to homepage, indicating a new user signup
            return redirect(url_for('homepage.homepage', new_user=True))

        except mysql.connector.Error as err:
            print(f"Database error during signup: {err}")
            # Rollback changes if an error occurs
            if 'conn' in locals() and conn.is_connected():
                conn.rollback()
            return render_template('signup.html', error='An error occurred during signup. Please try again.')

    else:
        # If user is already logged in, redirect to homepage
        if 'user_email' in session:
            return redirect(url_for('homepage.homepage'))
        return render_template('signup.html')

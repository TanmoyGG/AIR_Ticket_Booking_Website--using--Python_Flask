from flask import Blueprint, render_template, request, redirect, url_for, session, g, abort, flash, jsonify
from functools import wraps
import mysql.connector
import bcrypt # Import bcrypt for password hashing
import datetime # Import datetime for date handling
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt # Import Matplotlib (using Agg backend)
import os # Import os for path operations
import io # Import io for saving plots to memory
import base64 # Import base64 for embedding images

admin_bp = Blueprint('admin', __name__, url_prefix='/admin') # Add url_prefix for admin routes

# --- Decorator for Admin Access Control ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            return redirect(url_for('login.login_page', error="Admin access required."))
        return f(*args, **kwargs)
    return decorated_function

# --- Admin Routes ---

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard homepage."""
    user_name = session.get("user_name", "Admin")
    return render_template('admin/dashboard.html', user_name=user_name)

@admin_bp.route('/users')
@admin_required
def manage_users():
    """Display a list of all users."""
    users = []
    error = None
    try:
        if not hasattr(g, 'db_cursor') or g.db_cursor is None:
            raise Exception("Database connection not available.")

        cursor = g.db_cursor
        sql = "SELECT user_id, email AS userEmail, username AS userDetails_userName, role FROM Users ORDER BY user_id ASC"
        cursor.execute(sql)
        users = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching users for admin: {e}")
        error = "Could not retrieve user list."

    return render_template('admin/users.html', users=users, error=error)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Add a new user (Admin)."""
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        role = request.form.get('role') or 'user'
        if not username or not email or not password or not confirm:
            error = 'All fields are required.'
        elif password != confirm:
            error = 'Passwords do not match.'
        else:
            try:
                cursor = g.db_cursor; conn = g.db_conn
                cursor.execute('SELECT user_id FROM Users WHERE email=%s OR username=%s', (email, username))
                if cursor.fetchone():
                    error = 'Username or email already exists.'
                else:
                    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute(
                        'INSERT INTO Users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)',
                        (username, email, pw_hash, role)
                    )
                    conn.commit()
                    flash('New user added successfully.', 'success')
                    return redirect(url_for('admin.manage_users'))
            except mysql.connector.Error as err:
                conn.rollback()
                error = f'Database error: {err}'
    return render_template('admin/add_user.html', error=error)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit an existing user's details (Admin)."""
    error = None
    status = None
    user = None

    if not hasattr(g, 'db_cursor') or g.db_cursor is None or not hasattr(g, 'db_conn') or g.db_conn is None:
        return redirect(url_for('admin.manage_users', error="Database connection error."))

    cursor = g.db_cursor
    conn = g.db_conn

    try:
        cursor.execute(
            "SELECT user_id, email AS userEmail, username AS userDetails_userName, role FROM Users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        if not user:
            flash("User not found.", "error")
            return redirect(url_for('admin.manage_users'))
    except Exception as e:
        print(f"Error fetching user {user_id}: {e}")
        flash("Could not retrieve user details.", "error")
        return redirect(url_for('admin.manage_users'))

    if request.method == 'POST':
        new_name = request.form.get('name')
        new_email = request.form.get('email')
        new_role = request.form.get('role') or user['role']
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not new_name or not new_email:
            error = "Name and Email are required."
        elif new_password and new_password != confirm_password:
            error = "Passwords do not match."
        else:
            try:
                cursor.execute(
                    "SELECT user_id FROM Users WHERE email = %s AND user_id != %s",
                    (new_email, user_id)
                )
                if cursor.fetchone():
                    error = "Email address is already in use by another user."
                else:
                    if new_password:
                        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        cursor.execute(
                            "UPDATE Users SET username=%s, email=%s, role=%s, password_hash=%s WHERE user_id=%s",
                            (new_name, new_email, new_role, hashed, user_id)
                        )
                    else:
                        cursor.execute(
                            "UPDATE Users SET username=%s, email=%s, role=%s WHERE user_id=%s",
                            (new_name, new_email, new_role, user_id)
                        )
                    conn.commit()
                    status = "User details updated successfully."
                    return redirect(url_for('admin.manage_users', status=status))
            except mysql.connector.Error as err:
                conn.rollback()
                error = "Database error updating user."

    return render_template('admin/edit_user.html', user=user, error=error, status=status)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user account (Admin)."""
    error = None
    status = None

    logged_in_email = session.get('user_email')

    if not hasattr(g, 'db_cursor') or g.db_cursor is None or not hasattr(g, 'db_conn') or g.db_conn is None:
        flash("Database connection error.", "error")
        return redirect(url_for('admin.manage_users'))

    cursor = g.db_cursor
    conn = g.db_conn

    try:
        cursor.execute("SELECT email FROM Users WHERE user_id = %s", (user_id,))
        user_to_delete = cursor.fetchone()

        if not user_to_delete:
            flash("User not found.", "error")
            return redirect(url_for('admin.manage_users'))

        if logged_in_email == user_to_delete['email']:
             flash("Admins cannot delete their own account through this panel.", "error")
             return redirect(url_for('admin.manage_users'))

        sql_delete = "DELETE FROM Users WHERE user_id = %s"
        cursor.execute(sql_delete, (user_id,))
        conn.commit()

        if cursor.rowcount > 0:
            flash(f"User ID {user_id} deleted successfully.", "success")
        else:
            flash("User not found or already deleted.", "warning")

    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == 1451:
             print(f"FK Constraint Error deleting user {user_id}: {err}")
             flash(f"Cannot delete user ID {user_id}. They may have existing bookings. Please manage bookings first.", "error")
        else:
             print(f"Database error deleting user {user_id}: {err}")
             flash("Failed to delete user due to a database error.", "error")
    except Exception as e:
        conn.rollback()
        print(f"Error deleting user {user_id}: {e}")
        flash("An unexpected error occurred during deletion.", "error")

    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/timetable')
@admin_required
def manage_timetable():
    """Display the flight timetable for management."""
    flights = []
    error = None
    try:
        if not hasattr(g, 'db_cursor') or g.db_cursor is None:
            raise Exception("Database connection not available.")

        cursor = g.db_cursor
        sql = """
            SELECT
                fs.schedule_id AS flight_id,
                c1.name AS departure_city,
                c2.name AS arrival_city,
                fs.departure_time,
                fs.arrival_time,
                r.standard_fare AS economy_fare,
                r.standard_fare * 2 AS business_fare,
                fs.total_capacity,
                FLOOR(fs.total_capacity * 0.8) AS economy_capacity,
                CEIL(fs.total_capacity * 0.2) AS business_capacity
            FROM FlightSchedules fs
            JOIN Routes r ON fs.route_id = r.route_id
            JOIN Cities c1 ON r.departure_city_id = c1.city_id
            JOIN Cities c2 ON r.arrival_city_id = c2.city_id
            WHERE fs.is_active = TRUE
            ORDER BY c1.name, fs.departure_time
        """
        cursor.execute(sql)
        flights = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching timetable for admin: {e}")
        error = "Could not retrieve flight timetable."

    return render_template('admin/timetable.html', flights=flights, error=error)

@admin_bp.route('/schedule/add', methods=['GET', 'POST'])
@admin_required
def add_schedule():
    """Display form to add a new flight schedule and handle submission"""
    error = None
    if request.method == 'POST':
        dep_id = request.form.get('departure_city')
        arr_id = request.form.get('arrival_city')
        dep_time = request.form.get('departure_time')
        arr_time = request.form.get('arrival_time')
        total_cap = request.form.get('total_capacity') or 130
        is_active = 1 if request.form.get('is_active') == 'on' else 0
        if dep_id == arr_id:
            error = "Departure and arrival cities must differ."
        else:
            try:
                cursor = g.db_cursor; conn = g.db_conn
                cursor.execute(
                    "SELECT route_id FROM Routes WHERE departure_city_id=%s AND arrival_city_id=%s",
                    (dep_id, arr_id)
                )
                route = cursor.fetchone()
                if not route:
                    error = "Route not found. Please add the route first."
                else:
                    rid = route['route_id']
                    cursor.execute(
                        "INSERT INTO FlightSchedules(route_id, departure_time, arrival_time, total_capacity, is_active) VALUES(%s,%s,%s,%s,%s)",
                        (rid, dep_time, arr_time, total_cap, is_active)
                    )
                    conn.commit()
                    flash('New flight schedule added successfully.', 'success')
                    return redirect(url_for('admin.manage_timetable'))
            except mysql.connector.Error as err:
                conn.rollback()
                error = f"Database error: {err.msg}" if hasattr(err, 'msg') else f"Database error: {err}"
    try:
        cursor = g.db_cursor
        cursor.execute("SELECT city_id, name FROM Cities ORDER BY name")
        cities = cursor.fetchall()
    except Exception:
        cities = []
    return render_template('admin/add_schedule.html', cities=cities, error=error)

@admin_bp.route('/schedule/edit/<int:schedule_id>', methods=['GET', 'POST'])
@admin_required
def edit_schedule(schedule_id):
    """Display and process form to edit an existing flight schedule"""
    error = None
    cursor = g.db_cursor; conn = g.db_conn
    if request.method == 'POST':
        dep_id = request.form.get('departure_city')
        arr_id = request.form.get('arrival_city')
        dep_time = request.form.get('departure_time')
        arr_time = request.form.get('arrival_time')
        total_cap = request.form.get('total_capacity') or 130
        is_active = 1 if request.form.get('is_active') == 'on' else 0
        if dep_id == arr_id:
            error = "Departure and arrival cities must differ."
        else:
            try:
                cursor.execute(
                    "SELECT route_id FROM Routes WHERE departure_city_id=%s AND arrival_city_id=%s",
                    (dep_id, arr_id)
                )
                route = cursor.fetchone()
                if not route:
                    error = "Route not found. Please add the route first."
                else:
                    rid = route['route_id']
                    cursor.execute(
                        "UPDATE FlightSchedules SET route_id=%s, departure_time=%s, arrival_time=%s, total_capacity=%s, is_active=%s WHERE schedule_id=%s",
                        (rid, dep_time, arr_time, total_cap, is_active, schedule_id)
                    )
                    conn.commit()
                    flash('Flight schedule updated successfully.', 'success')
                    return redirect(url_for('admin.manage_timetable'))
            except mysql.connector.Error as err:
                conn.rollback()
                error = f"Database error: {err.msg if hasattr(err,'msg') else err}"
    cursor.execute(
        "SELECT fs.schedule_id, r.departure_city_id AS dep_id, r.arrival_city_id AS arr_id, fs.departure_time, fs.arrival_time, fs.total_capacity, fs.is_active "
        "FROM FlightSchedules fs JOIN Routes r ON fs.route_id=r.route_id WHERE fs.schedule_id=%s",
        (schedule_id,)
    )
    schedule = cursor.fetchone()
    if not schedule:
        flash('Schedule not found.', 'error')
        return redirect(url_for('admin.manage_timetable'))
    cursor.execute("SELECT city_id, name FROM Cities ORDER BY name")
    cities = cursor.fetchall()
    return render_template('admin/edit_schedule.html', schedule=schedule, cities=cities, error=error)

@admin_bp.route('/schedule/delete/<int:schedule_id>', methods=['POST'])
@admin_required
def delete_schedule(schedule_id):
    """Delete a flight schedule from the database (admin action)."""
    try:
        cursor = g.db_cursor
        conn = g.db_conn
        cursor.execute("DELETE FROM FlightSchedules WHERE schedule_id = %s", (schedule_id,))
        conn.commit()
        if cursor.rowcount > 0:
            flash(f"Flight schedule {schedule_id} deleted successfully.", "success")
        else:
            flash(f"Flight schedule {schedule_id} not found.", "warning")
    except mysql.connector.Error as err:
        conn.rollback()
        if hasattr(err, 'errno') and err.errno == 1451:
            flash("Cannot delete schedule; related instances or bookings exist.", "error")
        else:
            flash("Database error deleting schedule.", "error")
    except Exception:
        conn.rollback()
        flash("An unexpected error occurred deleting schedule.", "error")
    return redirect(url_for('admin.manage_timetable'))

@admin_bp.route('/cities')
@admin_required
def manage_cities():
    """List all cities."""
    error = None
    cities = []
    try:
        cursor = g.db_cursor
        cursor.execute("SELECT city_id, name FROM Cities ORDER BY name")
        cities = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching cities: {e}")
        error = "Could not load cities."
    return render_template('admin/cities.html', cities=cities, error=error)

@admin_bp.route('/cities/add', methods=['GET','POST'])
@admin_required
def add_city():
    """Add a new city."""
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            error = "City name required."
        else:
            try:
                cursor = g.db_cursor; conn = g.db_conn
                cursor.execute("INSERT INTO Cities(name) VALUES(%s)", (name,))
                conn.commit()
                flash("City added.", "success")
                return redirect(url_for('admin.manage_cities'))
            except mysql.connector.Error as err:
                conn.rollback()
                flash("Database error adding city.", "error")
    return render_template('admin/edit_city.html', city=None, error=error)

@admin_bp.route('/cities/edit/<int:city_id>', methods=['GET','POST'])
@admin_required
def edit_city(city_id):
    """Edit an existing city."""
    cursor = g.db_cursor; conn = g.db_conn
    cursor.execute("SELECT name FROM Cities WHERE city_id=%s", (city_id,))
    city = cursor.fetchone()
    if not city:
        flash("City not found.", "error")
        return redirect(url_for('admin.manage_cities'))
    error = None
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            error = "City name required."
        else:
            try:
                cursor.execute("UPDATE Cities SET name=%s WHERE city_id=%s", (name, city_id))
                conn.commit()
                flash("City updated.", "success")
                return redirect(url_for('admin.manage_cities'))
            except mysql.connector.Error:
                conn.rollback()
                flash("Database error updating city.", "error")
    return render_template('admin/edit_city.html', city={'city_id': city_id, 'name': city['name']}, error=error)

@admin_bp.route('/cities/delete/<int:city_id>', methods=['POST'])
@admin_required
def delete_city(city_id):
    """Delete a city."""
    cursor = g.db_cursor; conn = g.db_conn
    try:
        cursor.execute("DELETE FROM Cities WHERE city_id=%s", (city_id,))
        conn.commit()
        flash("City deleted.", "success")
    except mysql.connector.Error:
        conn.rollback()
        flash("Error deleting city (in use?).", "error")
    return redirect(url_for('admin.manage_cities'))

@admin_bp.route('/bookings')
@admin_required
def manage_bookings():
    """List all bookings for admin."""
    error = None
    bookings = []
    try:
        cursor = g.db_cursor
        sql = (
            "SELECT b.booking_id, u.username, u.email, c1.name AS departure_city, c2.name AS arrival_city, "
            "fi.departure_date, fs.departure_time, fs.arrival_time, b.seat_type, b.num_seats, b.total_price, b.status "
            "FROM Bookings b "
            "JOIN Users u ON b.user_id = u.user_id "
            "JOIN FlightInstances fi ON b.flight_instance_id = fi.flight_instance_id "
            "JOIN FlightSchedules fs ON fi.schedule_id = fs.schedule_id "
            "JOIN Routes r ON fs.route_id = r.route_id "
            "JOIN Cities c1 ON r.departure_city_id = c1.city_id "
            "JOIN Cities c2 ON r.arrival_city_id = c2.city_id "
            "ORDER BY fi.departure_date DESC, fs.departure_time"
        )
        cursor.execute(sql)
        bookings = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching bookings: {e}")
        error = "Could not load bookings."
    return render_template('admin/bookings.html', bookings=bookings, error=error)

@admin_bp.route('/bookings/update/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking_status(booking_id):
    """Update booking status (Confirmed/Cancelled) by admin."""
    new_status = request.form.get('status')
    try:
        cursor = g.db_cursor; conn = g.db_conn
        if new_status not in ['Confirmed', 'Cancelled', 'Pending']:
            flash('Invalid status.', 'error')
        else:
            cursor.execute("UPDATE Bookings SET status=%s WHERE booking_id=%s", (new_status, booking_id))
            conn.commit()
            flash(f'Booking {booking_id} updated to {new_status}.', 'success')
    except Exception as e:
        conn.rollback()
        print(f"Error updating booking {booking_id}: {e}")
        flash('Could not update booking status.', 'error')
    return redirect(url_for('admin.manage_bookings'))

@admin_bp.route('/reports')
@admin_required
def reports():
    """Display sales and customer reports with visualizations."""
    monthly_sales_data = []
    route_sales_data = []
    top_customers_data = []
    error = None
    monthly_sales_chart = None
    route_sales_chart = None
    top_customers_chart = None

    try:
        if not hasattr(g, 'db_cursor') or g.db_cursor is None:
            raise Exception("Database connection not available.")
        cursor = g.db_cursor

        # --- Monthly Sales ---
        sql_monthly = """
            SELECT DATE_FORMAT(booking_date, '%Y-%m') AS month, SUM(total_price) AS total_sales
            FROM Bookings
            WHERE status = 'Confirmed' -- Only count confirmed bookings
            GROUP BY month
            ORDER BY month ASC;
        """
        cursor.execute(sql_monthly)
        monthly_sales_data = cursor.fetchall()

        if monthly_sales_data:
            months = [row['month'] for row in monthly_sales_data]
            sales = [float(row['total_sales']) for row in monthly_sales_data]

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(months, sales, color='skyblue')
            ax.set_title('Monthly Sales (Confirmed Bookings)')
            ax.set_xlabel('Month')
            ax.set_ylabel('Total Sales (£)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            monthly_sales_chart = base64.b64encode(img.getvalue()).decode('utf8')
            plt.close(fig)

        # --- Sales by Route ---
        sql_route = """
            SELECT
                c1.name AS departure,
                c2.name AS arrival,
                SUM(b.total_price) AS total_sales
            FROM Bookings b
            JOIN FlightInstances fi ON b.flight_instance_id = fi.flight_instance_id
            JOIN FlightSchedules fs ON fi.schedule_id = fs.schedule_id
            JOIN Routes r ON fs.route_id = r.route_id
            JOIN Cities c1 ON r.departure_city_id = c1.city_id
            JOIN Cities c2 ON r.arrival_city_id = c2.city_id
            WHERE b.status = 'Confirmed' -- Only count confirmed bookings
            GROUP BY departure, arrival
            ORDER BY total_sales DESC
            LIMIT 10;
        """
        cursor.execute(sql_route)
        route_sales_data = cursor.fetchall()

        if route_sales_data:
            routes = [f"{row['departure']} -> {row['arrival']}" for row in route_sales_data]
            sales = [float(row['total_sales']) for row in route_sales_data]

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(routes, sales, color='lightcoral')
            ax.set_title('Top 10 Sales by Route (Confirmed Bookings)')
            ax.set_xlabel('Total Sales (£)')
            ax.set_ylabel('Route')
            plt.gca().invert_yaxis()
            plt.tight_layout()

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            route_sales_chart = base64.b64encode(img.getvalue()).decode('utf8')
            plt.close(fig)

        # --- Top Customers ---
        sql_customers = """
            SELECT u.username, u.email, SUM(b.total_price) AS total_spent
            FROM Bookings b
            JOIN Users u ON b.user_id = u.user_id
            WHERE b.status = 'Confirmed' -- Only count confirmed bookings
            GROUP BY u.user_id, u.username, u.email
            ORDER BY total_spent DESC
            LIMIT 10;
        """
        cursor.execute(sql_customers)
        top_customers_data = cursor.fetchall()

        if top_customers_data:
            customers = [row['username'] for row in top_customers_data]
            spent = [float(row['total_spent']) for row in top_customers_data]

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(customers, spent, color='mediumseagreen')
            ax.set_title('Top 10 Customers by Spending (Confirmed Bookings)')
            ax.set_xlabel('Customer Username')
            ax.set_ylabel('Total Spent (£)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            top_customers_chart = base64.b64encode(img.getvalue()).decode('utf8')
            plt.close(fig)

    except mysql.connector.Error as db_err:
        print(f"Database error fetching reports: {db_err}")
        error = f"Database error: {db_err}"
    except Exception as e:
        print(f"Error generating reports: {e}")
        error = "Could not generate reports."

    return render_template(
        'admin/reports.html',
        monthly_sales=monthly_sales_data,
        route_sales=route_sales_data,
        top_customers=top_customers_data,
        monthly_sales_chart=monthly_sales_chart,
        route_sales_chart=route_sales_chart,
        top_customers_chart=top_customers_chart,
        error=error
    )

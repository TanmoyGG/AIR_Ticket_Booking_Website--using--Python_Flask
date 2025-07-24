
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
import mysql.connector
import secrets
from routes.homepage import homepage_bp
from routes.flights import flights_bp
from routes.login import login_bp
from routes.account import account_bp
from routes.payment import payment_bp
from routes.signup import signup_bp
# from routes.visualization import visualization_bp  # Disabled Mongo-based visualization
from routes.admin import admin_bp  # Import the new admin blueprint

app = Flask(__name__, template_folder='templates')
app.secret_key = secrets.token_hex(16)

# MySQL connection setup
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with actual user
    'password': '12345',  # Replace with actual password
    'database': 'horizonairlines'  # Database name based on instructions
}

# Function to get a database connection and cursor
def get_db_cursor():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)  # Use dictionary cursor for easier row access
        return conn, cursor
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None, None

# Set up DB connection before each request
@app.before_request
def before_request():
    g.db_conn, g.db_cursor = get_db_cursor()
    if g.db_conn is None:
        print("Failed to get DB connection for request.")

# Tear down DB connection after each request
@app.teardown_request
def teardown_request(exception):
    cursor = getattr(g, 'db_cursor', None)
    if cursor:
        cursor.close()
    conn = getattr(g, 'db_conn', None)
    if conn:
        conn.close()

# Register the pages blueprint
app.register_blueprint(homepage_bp)
app.register_blueprint(flights_bp)
app.register_blueprint(login_bp)
app.register_blueprint(account_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(signup_bp)
# app.register_blueprint(visualization_bp)
app.register_blueprint(admin_bp)  # Register the admin blueprint

# Route to index.html when http://localhost:8080/ is accessed
@app.route('/')
def index():
    return render_template('login.html')

if __name__ == '__main__':
    # Check if database exists, create if not
    try:
        conn_check = mysql.connector.connect(host=db_config['host'], user=db_config['user'], password=db_config['password'])
        cursor_check = conn_check.cursor()
        cursor_check.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        cursor_check.close()
        conn_check.close()
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL or creating database: {err}")
        exit(1)

    # Load schema definitions from schema.sql
    try:
        conn_schema = mysql.connector.connect(**db_config)
        cursor_schema = conn_schema.cursor()
        with open('schema.sql', 'r') as f:
            schema_statements = f.read().split(';')
            for stmt in schema_statements:
                stmt = stmt.strip()
                if not stmt:
                    continue
                try:
                    cursor_schema.execute(stmt)
                except mysql.connector.Error as err:
                    # Ignore 'table already exists' and 'duplicate key name' errors
                    if err.errno in (1050, 1061):
                        continue
                    else:
                        raise
        conn_schema.commit()
        cursor_schema.close()
        conn_schema.close()
        print("Database schema loaded from schema.sql (duplicates ignored)")
    except Exception as e:
        print(f"Error loading database schema: {e}")
        exit(1)

    # Seed initial data for Cities, Routes, and FlightSchedules
    try:
        seed_conn = mysql.connector.connect(**db_config)
        seed_cur = seed_conn.cursor()
        # Timetable entries: (dep, arr, dep_time, arr_time)
        timetable = [
            ('Newcastle','Bristol','17:45:00','19:00:00'),
            ('Bristol','Newcastle','09:00:00','10:15:00'),
            ('Cardiff','Edinburgh','07:00:00','08:30:00'),
            ('Bristol','Manchester','12:30:00','13:30:00'),
            ('Manchester','Bristol','13:20:00','14:20:00'),
            ('Bristol','London','07:40:00','08:20:00'),
            ('London','Manchester','13:00:00','14:00:00'),
            ('Manchester','Glasgow','12:20:00','13:30:00'),
            ('Bristol','Glasgow','08:40:00','09:45:00'),
            ('Glasgow','Newcastle','14:30:00','15:45:00'),
            ('Newcastle','Manchester','16:15:00','17:05:00'),
            ('Manchester','Bristol','18:25:00','19:30:00'),
            ('Bristol','Manchester','06:20:00','07:20:00'),
            ('Portsmouth','Dundee','12:00:00','14:00:00'),
            ('Dundee','Portsmouth','10:00:00','12:00:00'),
            ('Edinburgh','Cardiff','18:30:00','20:00:00'),
            ('Southampton','Manchester','12:00:00','13:30:00'),
            ('Manchester','Southampton','19:00:00','20:30:00'),
            ('Birmingham','Newcastle','17:00:00','17:45:00'),
            ('Newcastle','Birmingham','07:00:00','07:45:00'),
            ('Aberdeen','Portsmouth','08:00:00','09:30:00'),
        ]
        # Helper to get standard fare
        fare_map = {frozenset(['Dundee','Portsmouth']):120,
                    frozenset(['Bristol','Manchester']):80,
                    frozenset(['Bristol','Newcastle']):90,
                    frozenset(['Bristol','Glasgow']):110,
                    frozenset(['Bristol','London']):80,
                    frozenset(['Manchester','Southampton']):90,
                    frozenset(['Cardiff','Edinburgh']):90}
        def get_fare(a,b):
            key = frozenset([a,b])
            return fare_map.get(key,100)
        # Seed Cities
        seed_cur.execute("SELECT COUNT(*) FROM Cities")
        if seed_cur.fetchone()[0] == 0:
            cities = set([d for (d,_,_,_) in timetable] + [a for (_,a,_,_) in timetable])
            for city in cities:
                seed_cur.execute("INSERT INTO Cities(name) VALUES(%s)", (city,))
            seed_conn.commit()
        # Build city_id map
        seed_cur.execute("SELECT city_id, name FROM Cities")
        city_map = {name:cid for cid,name in seed_cur.fetchall()}
        # Seed Routes
        for dep,arr,_,_ in timetable:
            dep_id = city_map[dep]; arr_id = city_map[arr]
            fare = get_fare(dep,arr)
            seed_cur.execute("INSERT IGNORE INTO Routes(departure_city_id,arrival_city_id,standard_fare) VALUES(%s,%s,%s)",
                             (dep_id,arr_id,fare))
        seed_conn.commit()
        # Build route_id map
        seed_cur.execute("SELECT route_id, departure_city_id, arrival_city_id FROM Routes")
        route_map = { (dep,arr):rid for rid,dep,arr in seed_cur.fetchall() }
        # Seed FlightSchedules
        seed_cur.execute("SELECT COUNT(*) FROM FlightSchedules")
        if seed_cur.fetchone()[0] == 0:
            for dep,arr,dt,at in timetable:
                rid = route_map[(city_map[dep],city_map[arr])]
                seed_cur.execute(
                    "INSERT INTO FlightSchedules(route_id,departure_time,arrival_time,total_capacity,is_active) VALUES(%s,%s,%s,130,1)",
                    (rid,dt,at)
                )
            seed_conn.commit()
        seed_cur.close(); seed_conn.close()
    except Exception as e:
        print(f"Error seeding initial data: {e}")
    # Run the app
    app.run(debug=True, port=8080)

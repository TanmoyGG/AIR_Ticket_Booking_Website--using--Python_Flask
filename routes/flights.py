from flask import Blueprint, render_template, request, redirect, url_for, session, g
import mysql.connector
from datetime import date, timedelta, datetime  # Add datetime
from decimal import Decimal

flights_bp = Blueprint('flights', __name__)

@flights_bp.route("/search-flights", methods=["GET", "POST"])
def search_flights():
    user_name = session.get("user_name")
    user_email = session.get("user_email")
    from_locations = []
    to_locations = []
    schedules = []
    search_message = ""
    from_city = ""
    to_city = ""
    all_routes = []  # List of all available flight routes for display

    # Default travel parameters
    travel_date = None
    num_seats = 1
    seat_type = 'Economy'

    # Ensure DB connection
    if not hasattr(g, 'db_cursor') or g.db_cursor is None:
        return render_template("flights.html", error="Database connection error.", user_name=user_name, user_email=user_email)
    cursor = g.db_cursor

    # Populate departure/arrival dropdowns from Routes and Cities
    cursor.execute(
        "SELECT DISTINCT c.name AS city "
        "FROM Routes r JOIN Cities c ON r.departure_city_id = c.city_id "
        "ORDER BY city"
    )
    from_locations = [row['city'] for row in cursor.fetchall()]
    cursor.execute(
        "SELECT DISTINCT c.name AS city "
        "FROM Routes r JOIN Cities c ON r.arrival_city_id = c.city_id "
        "ORDER BY city"
    )
    to_locations = [row['city'] for row in cursor.fetchall()]

    # Populate all routes for overview section
    cursor.execute(
        "SELECT DISTINCT c1.name AS departure, c2.name AS arrival "
        "FROM Routes r "
        "JOIN Cities c1 ON r.departure_city_id = c1.city_id "
        "JOIN Cities c2 ON r.arrival_city_id = c2.city_id "
        "ORDER BY c1.name, c2.name"
    )
    all_routes = cursor.fetchall()

    if request.method == "POST":
        # Read travel parameters
        travel_date = request.form.get("travel_date")
        num_seats = int(request.form.get("num_seats", 1))
        seat_type = request.form.get("seat_type", 'Economy')
        from_city = request.form.get("from_location")
        to_city = request.form.get("to_location")
        search_message = ""

        # Build query for schedules
        base_query = (
            "SELECT fs.schedule_id, c1.name AS departure_city, fs.departure_time, "
            "c2.name AS arrival_city, fs.arrival_time, r.standard_fare "
            "FROM Routes r "
            "JOIN Cities c1 ON r.departure_city_id = c1.city_id "
            "JOIN Cities c2 ON r.arrival_city_id = c2.city_id "
            "JOIN FlightSchedules fs ON fs.route_id = r.route_id "
            "WHERE 1=1"
        )
        params = []
        if from_city:
            base_query += " AND c1.name = %s"
            params.append(from_city)
        if to_city:
            base_query += " AND c2.name = %s"
            params.append(to_city)

        if from_city or to_city:
            cursor.execute(base_query, tuple(params))
            schedules = cursor.fetchall()
            if schedules:
                search_message = "Showing flights"
                if from_city: search_message += f" from {from_city}"
                if to_city: search_message += f" to {to_city}"
            else:
                search_message = "No flights found matching your criteria."
        else:
            search_message = "Please select a departure or arrival city."

        # Calculate booking discounts and pricing for each schedule
        if schedules and travel_date:
            travel_dt = date.fromisoformat(travel_date)
            today = date.today()
            for s in schedules:
                # Determine base per-seat price using Decimal for calculations
                seat_multiplier = Decimal(1) if seat_type == 'Economy' else Decimal(2)
                base_price = s['standard_fare'] * seat_multiplier
                days = (travel_dt - today).days
                if 80 <= days <= 90:
                    disc = Decimal(25)
                elif 60 <= days <= 79:
                    disc = Decimal(15)
                elif 45 <= days <= 59:
                    disc = Decimal(10)
                else:
                    disc = Decimal(0)
                # Apply discount multiplier as Decimal
                multiplier = (Decimal(100) - disc) / Decimal(100)
                total = (base_price * Decimal(num_seats)) * multiplier
                # Store formatted values
                s['price_per_seat'] = base_price
                # Total before discount
                s['total_before_discount'] = (base_price * Decimal(num_seats)).quantize(Decimal('0.01'))
                s['discount_pct'] = int(disc)
                s['total_price'] = total.quantize(Decimal('0.01'))

    # Compute date pickers for template
    today_str = date.today().isoformat()
    max_str = (date.today() + timedelta(days=90)).isoformat()

    return render_template(
        "flights.html",
        from_locations=from_locations,
        to_locations=to_locations,
        schedules=schedules,
        search_message=search_message,
        user_name=user_name,
        user_email=user_email,
        today=today_str,
        max_date=max_str,
        travel_date=travel_date,
        num_seats=num_seats,
        seat_type=seat_type,
        now=datetime.utcnow(),  # Pass datetime object for footer year
        all_routes=all_routes
    )
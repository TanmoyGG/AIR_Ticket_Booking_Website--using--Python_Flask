
from flask import Blueprint, render_template, request, redirect, url_for, session, g, send_file
import mysql.connector
from datetime import datetime, date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import navy, grey, black, white

payment_bp = Blueprint('payment', __name__)

@payment_bp.route("/payment", methods=["GET"])
def payment():
    if 'user_email' not in session:
        return redirect(url_for('login.login_page', error="Please log in to proceed with payment."))

    # Get parameters from request
    schedule_id = request.args.get('schedule_id')
    travel_date = request.args.get('travel_date')  # YYYY-MM-DD
    num_seats = int(request.args.get('num_seats', 0))
    seat_type = request.args.get('seat_type')  # 'Economy' or 'Business'

    # Fetch fare and route details
    cursor = g.db_cursor
    sql = (
        "SELECT r.standard_fare, c1.name AS departure_city, c2.name AS arrival_city, fs.total_capacity "
        "FROM FlightSchedules fs "
        "JOIN Routes r ON fs.route_id = r.route_id "
        "JOIN Cities c1 ON r.departure_city_id = c1.city_id "
        "JOIN Cities c2 ON r.arrival_city_id = c2.city_id "
        "WHERE fs.schedule_id = %s"
    )
    cursor.execute(sql, (schedule_id,))
    row = cursor.fetchone()
    if not row:
        return redirect(url_for('flights.search_flights', error="Invalid flight selection."))

    base_fare = Decimal(row['standard_fare'])
    if seat_type == 'Business':
        fare_per_seat = base_fare * 2
    else:
        fare_per_seat = base_fare

    total_base = fare_per_seat * num_seats
    days = (date.fromisoformat(travel_date) - date.today()).days
    # discount logic
    if 80 <= days <= 90:
        discount = Decimal('0.25')
    elif 60 <= days <= 79:
        discount = Decimal('0.15')
    elif 45 <= days <= 59:
        discount = Decimal('0.10')
    else:
        discount = Decimal('0.00')
    disc_amt = (total_base * discount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    final_price = (total_base - disc_amt).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # store details
    session['pay'] = {
        'schedule_id': schedule_id,
        'travel_date': travel_date,
        'num_seats': num_seats,
        'seat_type': seat_type,
        'fare_per_seat': str(fare_per_seat),
        'discount_percent': str(int(discount * 100)),
        'total_price': str(final_price)
    }

    return render_template('payment.html', schedule_id=schedule_id,
                           departure_city=row['departure_city'], arrival_city=row['arrival_city'],
                           travel_date=travel_date, num_seats=num_seats, seat_type=seat_type,
                           fare_per_seat=fare_per_seat, discount_percent=int(discount*100),
                           total_price=final_price)

@payment_bp.route("/confirm-payment", methods=["POST"])
def confirm_payment():
    if 'user_email' not in session or 'pay' not in session:
        return redirect(url_for('login.login_page', error="Session expired."))
    pay = session['pay']
    user_email = session['user_email']
    # get user_id
    cursor = g.db_cursor; conn = g.db_conn
    cursor.execute("SELECT user_id FROM Users WHERE email=%s", (user_email,))
    u = cursor.fetchone()
    user_id = u['user_id']

    schedule_id = pay['schedule_id']; travel_date = pay['travel_date']
    num_seats = pay['num_seats']; seat_type = pay['seat_type']
    total_price = Decimal(pay['total_price'])

    # lock instance row
    cursor.execute(
        "SELECT flight_instance_id, available_economy_seats, available_business_seats "
        "FROM FlightInstances WHERE schedule_id=%s AND departure_date=%s FOR UPDATE",
        (schedule_id, travel_date)
    )
    inst = cursor.fetchone()
    if not inst:
        # create instance availability
        # get total_capacity
        cursor.execute("SELECT total_capacity FROM FlightSchedules WHERE schedule_id=%s", (schedule_id,))
        tc = cursor.fetchone()['total_capacity']
        bus_cap = int(tc * 0.2)
        eco_cap = tc - bus_cap
        inst_sql = "INSERT INTO FlightInstances(schedule_id, departure_date, available_economy_seats, available_business_seats) VALUES(%s,%s,%s,%s)"
        cursor.execute(inst_sql, (schedule_id, travel_date, eco_cap, bus_cap))
        flight_instance_id = cursor.lastrowid
        available_eco = eco_cap; available_bus = bus_cap
    else:
        flight_instance_id = inst['flight_instance_id']
        available_eco = inst['available_economy_seats']; available_bus = inst['available_business_seats']
    # check availability
    if seat_type=='Economy' and num_seats>available_eco or seat_type=='Business' and num_seats>available_bus:
        conn.rollback()
        return redirect(url_for('flights.search_flights', error='Not enough seats available.'))
    # deduct seats
    if seat_type=='Economy':
        cursor.execute("UPDATE FlightInstances SET available_economy_seats=available_economy_seats-%s WHERE flight_instance_id=%s",
                       (num_seats, flight_instance_id))
    else:
        cursor.execute("UPDATE FlightInstances SET available_business_seats=available_business_seats-%s WHERE flight_instance_id=%s",
                       (num_seats, flight_instance_id))
    # insert booking and get booking_id
    book_sql = ("INSERT INTO Bookings(user_id, flight_instance_id, num_seats, seat_type, total_price, status) "
                "VALUES(%s,%s,%s,%s,%s,'Confirmed')")
    cursor.execute(book_sql, (user_id, flight_instance_id, num_seats, seat_type, total_price))
    booking_id = cursor.lastrowid
    conn.commit()
    # Compute total before discount for receipt
    price_per_seat = Decimal(pay['fare_per_seat'])
    seats_qty = Decimal(pay['num_seats'])
    total_before = (price_per_seat * seats_qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # --- Enhanced PDF Receipt Generation ---
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdf.setTitle(f"BookingReceipt_{booking_id}")

    # Header
    pdf.setFillColor(navy)
    pdf.rect(0, height - 1.5*inch, width, 1.5*inch, fill=1, stroke=0)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(width/2, height - 0.75*inch, "Horizon Airlines")
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width/2, height - 1.1*inch, "Booking Confirmation Receipt")

    # Content Area
    pdf.setFillColor(black)
    y = height - 2*inch

    # Booking Details Section
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(1*inch, y, "Booking Details")
    y -= 0.3*inch
    pdf.setStrokeColor(grey)
    pdf.line(1*inch, y, width - 1*inch, y)
    y -= 0.5*inch

    pdf.setFont("Helvetica", 11)
    booking_details = [
        ("Booking ID:", f"{booking_id}"),
        ("User Email:", f"{session['user_email']}"),
        ("Flight Instance ID:", f"{flight_instance_id}"),
        ("Travel Date:", f"{travel_date}"),
        ("Number of Seats:", f"{num_seats}"),
        ("Seat Class:", f"{seat_type}"),
        ("Booking Date:", f"{datetime.now().strftime('%d %B %Y %H:%M')}")
    ]
    for label, value in booking_details:
        pdf.drawString(1.5*inch, y, label)
        pdf.drawString(3.5*inch, y, value)
        y -= 0.25*inch

    y -= 0.5*inch

    # Payment Summary Section
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(1*inch, y, "Payment Summary")
    y -= 0.3*inch
    pdf.setStrokeColor(grey)
    pdf.line(1*inch, y, width - 1*inch, y)
    y -= 0.5*inch

    pdf.setFont("Helvetica", 11)
    payment_details = [
        ("Price per Seat:", f"£{pay['fare_per_seat']}"),
        ("Total Before Discount:", f"£{total_before:.2f}"),
        ("Discount Applied:", f"{pay['discount_percent']}%"),
        ("Final Amount Paid:", f"£{pay['total_price']}"),
    ]
    for label, value in payment_details:
        pdf.drawString(1.5*inch, y, label)
        pdf.drawString(3.5*inch, y, value)
        y -= 0.25*inch

    # Footer
    y = 1.5*inch
    pdf.setStrokeColor(grey)
    pdf.line(1*inch, y, width - 1*inch, y)
    y -= 0.3*inch
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.setFillColor(grey)
    pdf.drawCentredString(width/2, y, "Thank you for booking with Horizon Airlines!")
    y -= 0.2*inch
    pdf.drawCentredString(width/2, y, "We wish you a pleasant journey.")

    # --- End Enhanced PDF Receipt Generation ---

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    session.pop('pay', None)
    # Return PDF as downloadable file
    return send_file(buffer,
                     as_attachment=True,
                     download_name=f"BookingReceipt_{booking_id}.pdf",
                     mimetype='application/pdf')

@payment_bp.route("/book-flight", methods=["GET"])
def book_flight():
    """Book a flight and redirect to homepage with confirmation."""
    if 'user_email' not in session:
        return redirect(url_for('login.login_page', error="Please log in to book."))

    # Read booking params
    schedule_id = request.args.get('schedule_id')
    travel_date = request.args.get('travel_date')
    num_seats = int(request.args.get('num_seats', 1))
    seat_type = request.args.get('seat_type', 'Economy')

    # Get user_id
    cursor = g.db_cursor; conn = g.db_conn
    cursor.execute("SELECT user_id FROM Users WHERE email=%s", (session['user_email'],))
    u = cursor.fetchone()
    if not u:
        return redirect(url_for('login.login_page', error="Invalid user."))
    user_id = u['user_id']

    # Lock or create instance
    cursor.execute(
        "SELECT flight_instance_id, available_economy_seats, available_business_seats "
        "FROM FlightInstances WHERE schedule_id=%s AND departure_date=%s FOR UPDATE",
        (schedule_id, travel_date)
    )
    inst = cursor.fetchone()
    if not inst:
        # create availability based on schedule capacity
        cursor.execute("SELECT total_capacity FROM FlightSchedules WHERE schedule_id=%s", (schedule_id,))
        tc = cursor.fetchone()['total_capacity']
        bus_cap = int(tc * 0.2)
        eco_cap = tc - bus_cap
        cursor.execute(
            "INSERT INTO FlightInstances(schedule_id, departure_date, available_economy_seats, available_business_seats) "
            "VALUES(%s,%s,%s,%s)",
            (schedule_id, travel_date, eco_cap, bus_cap)
        )
        flight_instance_id = cursor.lastrowid
        available_eco, available_bus = eco_cap, bus_cap
    else:
        flight_instance_id = inst['flight_instance_id']
        available_eco, available_bus = inst['available_economy_seats'], inst['available_business_seats']

    # Check & deduct seats
    if (seat_type=='Economy' and num_seats>available_eco) or (seat_type=='Business' and num_seats>available_bus):
        conn.rollback()
        return redirect(url_for('flights.search_flights', error='Not enough seats.'))
    if seat_type=='Economy':
        cursor.execute(
            "UPDATE FlightInstances SET available_economy_seats=available_economy_seats-%s WHERE flight_instance_id=%s",
            (num_seats, flight_instance_id)
        )
    else:
        cursor.execute(
            "UPDATE FlightInstances SET available_business_seats=available_business_seats-%s WHERE flight_instance_id=%s",
            (num_seats, flight_instance_id)
        )

    # Compute base per-seat price
    cursor.execute(
        "SELECT r.standard_fare FROM FlightSchedules fs JOIN Routes r ON fs.route_id=r.route_id WHERE fs.schedule_id=%s",
        (schedule_id,)
    )
    base_fare = Decimal(cursor.fetchone()['standard_fare'])
    price_per = base_fare * (Decimal(2) if seat_type=='Business' else Decimal(1))
    # Calculate discount based on days in advance
    days = (date.fromisoformat(travel_date) - date.today()).days
    if 80 <= days <= 90:
        disc = Decimal('0.25')
    elif 60 <= days <= 79:
        disc = Decimal('0.15')
    elif 45 <= days <= 59:
        disc = Decimal('0.10')
    else:
        disc = Decimal('0.00')
    # Calculate final total price after discount
    total_base = price_per * Decimal(num_seats)
    total_price = (total_base * (Decimal(1) - disc)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    # Compute total before discount for booking shortcut
    total_before = (price_per * Decimal(num_seats)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    # Insert booking record and get booking_id
    insert_sql = (
        "INSERT INTO Bookings(user_id, flight_instance_id, num_seats, seat_type, total_price, status) "
        "VALUES (%s, %s, %s, %s, %s, 'Confirmed')"
    )
    cursor.execute(insert_sql, (user_id, flight_instance_id, num_seats, seat_type, total_price))
    booking_id = cursor.lastrowid
    conn.commit()

    # --- Enhanced PDF Receipt Generation (book_flight shortcut) ---
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdf.setTitle(f"BookingReceipt_{booking_id}")

    # Header
    pdf.setFillColor(navy)
    pdf.rect(0, height - 1.5*inch, width, 1.5*inch, fill=1, stroke=0)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(width/2, height - 0.75*inch, "Horizon Airlines")
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width/2, height - 1.1*inch, "Booking Confirmation Receipt")

    # Content Area
    pdf.setFillColor(black)
    y = height - 2*inch

    # Booking Details Section
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(1*inch, y, "Booking Details")
    y -= 0.3*inch
    pdf.setStrokeColor(grey)
    pdf.line(1*inch, y, width - 1*inch, y)
    y -= 0.5*inch

    pdf.setFont("Helvetica", 11)
    booking_details = [
        ("Booking ID:", f"{booking_id}"),
        ("User Email:", f"{session['user_email']}"),
        ("Flight Instance ID:", f"{flight_instance_id}"),
        ("Travel Date:", f"{travel_date}"),
        ("Number of Seats:", f"{num_seats}"),
        ("Seat Class:", f"{seat_type}"),
        ("Booking Date:", f"{datetime.now().strftime('%d %B %Y %H:%M')}")
    ]
    for label, value in booking_details:
        pdf.drawString(1.5*inch, y, label)
        pdf.drawString(3.5*inch, y, value)
        y -= 0.25*inch

    y -= 0.5*inch

    # Payment Summary Section
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(1*inch, y, "Payment Summary")
    y -= 0.3*inch
    pdf.setStrokeColor(grey)
    pdf.line(1*inch, y, width - 1*inch, y)
    y -= 0.5*inch

    pdf.setFont("Helvetica", 11)
    payment_details = [
        ("Price per Seat:", f"£{price_per:.2f}"),
        ("Total Before Discount:", f"£{total_before:.2f}"),
        ("Discount Applied:", f"{int(disc*100)}%"),
        ("Final Amount Paid:", f"£{total_price:.2f}"),
    ]
    for label, value in payment_details:
        pdf.drawString(1.5*inch, y, label)
        pdf.drawString(3.5*inch, y, value)
        y -= 0.25*inch

    # Footer
    y = 1.5*inch
    pdf.setStrokeColor(grey)
    pdf.line(1*inch, y, width - 1*inch, y)
    y -= 0.3*inch
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.setFillColor(grey)
    pdf.drawCentredString(width/2, y, "Thank you for booking with Horizon Airlines!")
    y -= 0.2*inch
    pdf.drawCentredString(width/2, y, "We wish you a pleasant journey.")

    # --- End Enhanced PDF Receipt Generation ---

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return send_file(buffer,
                     as_attachment=True,
                     download_name=f"BookingReceipt_{booking_id}.pdf",
                     mimetype='application/pdf')

from flask import Blueprint, render_template, request, redirect, url_for, session, g, send_file
import mysql.connector
from datetime import datetime, date
from decimal import Decimal
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import navy, grey, black, white

# homepage blueprint
homepage_bp = Blueprint('homepage', __name__)

@homepage_bp.route('/homepage')
def homepage():
    if 'user_email' not in session:
        return redirect(url_for('login.login_page', error="Please log in to view the homepage."))

    user_email = session['user_email']
    user_name = session.get('user_name')  # for greeting
    conn = g.db_conn
    cursor = g.db_cursor

    # fetch user_id
    cursor.execute("SELECT user_id FROM Users WHERE email=%s", (user_email,))
    u = cursor.fetchone()
    user_id = u['user_id'] if u else None

    bookings = []
    status = request.args.get('status')
    error = request.args.get('error')
    has_bookings = False

    if user_id:
        sql = (
            "SELECT b.booking_id, c1.name AS departure_city, c2.name AS arrival_city, fi.departure_date, "
            "fs.departure_time, fs.arrival_time, b.seat_type, b.num_seats, b.total_price, b.status "
            "FROM Bookings b "
            "JOIN FlightInstances fi ON b.flight_instance_id = fi.flight_instance_id "
            "JOIN FlightSchedules fs ON fi.schedule_id = fs.schedule_id "
            "JOIN Routes r ON fs.route_id = r.route_id "
            "JOIN Cities c1 ON r.departure_city_id = c1.city_id "
            "JOIN Cities c2 ON r.arrival_city_id = c2.city_id "
            "WHERE b.user_id = %s AND b.status != 'Cancelled' "
            "ORDER BY fi.departure_date, fs.departure_time"
        )
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        for row in rows:
            # Convert row to a mutable dictionary
            booking_dict = dict(row)
            # Format departure_time (timedelta) to HH:MM string
            if booking_dict.get('departure_time'):
                # timedelta string format is HH:MM:SS, slice to get HH:MM
                booking_dict['departure_time_str'] = str(booking_dict['departure_time'])[:-3]
            else:
                booking_dict['departure_time_str'] = 'N/A'
            bookings.append(booking_dict) # Append the dictionary
        has_bookings = bool(bookings)

    return render_template('homepage.html', bookings=bookings, has_bookings=has_bookings,
                           user_email=user_email, user_name=user_name, status=status, error=error)

@homepage_bp.route('/cancel-booking', methods=['POST'])
def cancel_booking():
    booking_id = request.form.get('booking_id')
    user_email = session.get('user_email')
    conn = g.db_conn
    cursor = g.db_cursor

    # fetch booking and related details for refund calculation
    cursor.execute(
        "SELECT b.user_id, b.flight_instance_id, b.num_seats, b.seat_type, b.total_price, fi.departure_date "
        "FROM Bookings b "
        "JOIN FlightInstances fi ON b.flight_instance_id=fi.flight_instance_id "
        "JOIN Users u ON b.user_id=u.user_id "
        "WHERE b.booking_id=%s AND u.email=%s",
        (booking_id, user_email)
    )
    bk = cursor.fetchone()
    if not bk:
        return redirect(url_for('homepage.homepage', error='Booking not found.'))

    # update booking status
    cursor.execute("UPDATE Bookings SET status='Cancelled' WHERE booking_id=%s", (booking_id,))

    # restore seats
    if bk['seat_type'] == 'Economy':
        cursor.execute(
            "UPDATE FlightInstances SET available_economy_seats=available_economy_seats+%s WHERE flight_instance_id=%s",
            (bk['num_seats'], bk['flight_instance_id'])
        )
    else:
        cursor.execute(
            "UPDATE FlightInstances SET available_business_seats=available_business_seats+%s WHERE flight_instance_id=%s",
            (bk['num_seats'], bk['flight_instance_id'])
        )

    conn.commit()

    # Calculate cancellation fee and refund
    total_price = Decimal(bk['total_price'])
    departure_date = bk['departure_date']
    days_before = (departure_date - date.today()).days
    if days_before > 60:
        fee_pct = Decimal('0.00')
    elif days_before > 30:
        fee_pct = Decimal('0.40')
    else:
        fee_pct = Decimal('1.00')
    fee_amount = (total_price * fee_pct).quantize(Decimal('0.01'))
    refund_amount = (total_price - fee_amount).quantize(Decimal('0.01'))

    # Generate PDF cancellation receipt
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdf.setTitle(f"CancellationReceipt_{booking_id}")

    # --- Enhanced Styling ---

    # Header
    pdf.setFillColor(navy)
    pdf.rect(0, height - 1.5*inch, width, 1.5*inch, fill=1, stroke=0)
    pdf.setFillColor(white)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(width/2, height - 0.75*inch, "Horizon Airlines")
    pdf.setFont("Helvetica", 14)
    pdf.drawCentredString(width/2, height - 1.1*inch, "Booking Cancellation Receipt")

    # Content Area
    pdf.setFillColor(black)
    pdf.setFont("Helvetica-Bold", 16)
    y = height - 2*inch
    pdf.drawString(1*inch, y, "Cancellation Details")
    y -= 0.3*inch
    pdf.setStrokeColor(grey)
    pdf.line(1*inch, y, width - 1*inch, y)
    y -= 0.5*inch

    pdf.setFont("Helvetica", 11)
    details = [
        ("Booking ID:", f"{booking_id}"),
        ("Flight Instance ID:", f"{bk['flight_instance_id']}"),
        ("Original Travel Date:", f"{departure_date.strftime('%d %B %Y')}"),
        ("Cancellation Date:", f"{date.today().strftime('%d %B %Y')}"),
        ("Days Before Departure:", f"{days_before}"),
    ]
    for label, value in details:
        pdf.drawString(1.5*inch, y, label)
        pdf.drawString(3.5*inch, y, value)
        y -= 0.25*inch

    y -= 0.5*inch
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(1*inch, y, "Financial Summary")
    y -= 0.3*inch
    pdf.setStrokeColor(grey)
    pdf.line(1*inch, y, width - 1*inch, y)
    y -= 0.5*inch

    pdf.setFont("Helvetica", 11)
    financials = [
        ("Total Amount Paid:", f"£{total_price:.2f}"),
        ("Cancellation Fee Percentage:", f"{int(fee_pct*100)}%"),
        ("Cancellation Fee Amount:", f"£{fee_amount:.2f}"),
        ("Refund Amount:", f"£{refund_amount:.2f}"),
    ]
    for label, value in financials:
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
    pdf.drawCentredString(width/2, y, "Thank you for choosing Horizon Airlines.")
    y -= 0.2*inch
    pdf.drawCentredString(width/2, y, "Please contact customer support if you have any questions.")

    # --- End Enhanced Styling ---

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return send_file(buffer,
                     as_attachment=True,
                     download_name=f"CancellationReceipt_{booking_id}.pdf",
                     mimetype='application/pdf')

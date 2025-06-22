from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages!

feedbacks = []

def init_db():
    # BOOKINGS DB
    conn = sqlite3.connect('admin_bookings.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resort_name TEXT,
            guest_first_name TEXT,
            guest_last_name TEXT,
            checkin_date TEXT,
            checkin_time TEXT,
            checkout_date TEXT,
            checkout_time TEXT,
            nights INTEGER,
            room_type TEXT,
            guests INTEGER,
            special_requests TEXT,
            payment_method TEXT,
            total_amount REAL,
            downpayment REAL,
            remaining_balance REAL,
            status TEXT,
            qr_path TEXT,
            reference_number TEXT,
            bank_number_last4 TEXT,
            card_holder_name TEXT,
            bank_reference_number TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

    # FEEDBACK DB
    # Now create feedback.db if not exists and table
    conn_fb = sqlite3.connect('feedback.db')
    conn_fb.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resort_name TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conn_fb.commit()
    conn_fb.close()

def get_db_connection():
    conn = sqlite3.connect('admin_bookings.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_feedback_db_connection():
    conn = sqlite3.connect('feedback.db')
    conn.row_factory = sqlite3.Row
    return conn

def fetch_bookings(resort_name=None):
    conn = get_db_connection()
    sql = "SELECT * FROM admin_bookings"
    params = ()
    if resort_name:
        sql += " WHERE resort_name = ?"
        params = (resort_name,)
    sql += " ORDER BY created_at DESC"
    bookings = conn.execute(sql, params).fetchall()
    conn.close()
    return bookings

def get_all_feedbacks():
    conn = get_feedback_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT resort_name, message FROM feedback ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    resort = request.form.get('resort')
    message = request.form.get('message')
    if resort and message:
        conn = get_feedback_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO feedback (resort_name, message) VALUES (?, ?)", (resort, message))
        conn.commit()
        conn.close()
        flash("Thank you for your feedback!", "success")
    else:
        flash("Please select a resort and enter your feedback.", "danger")
    return redirect(url_for('homepage'))

@app.route('/2ndpage')
def explore():
    return render_template('2ndpage.html')

@app.route('/resort-details')
def resort_details():
    resort = request.args.get('resort')
    # Get all feedbacks from db
    all_feedbacks = get_all_feedbacks()
    # Filter for the selected resort
    feedbacks = []
    for fb in all_feedbacks:
        # fb['resort_name'] is the value saved in the db, e.g. "bluewave-pool-resort"
        if fb['resort_name'] == resort:
            feedbacks.append({'resort': fb['resort_name'], 'message': fb['message']})
    return render_template('3rdpage.html', resort=resort, feedbacks=feedbacks)

@app.route('/finalbookingform.html')
def finalbookingform():
    resort = request.args.get('resort', '')
    checkin = request.args.get('checkin', '')
    checkout = request.args.get('checkout', '')
    location = request.args.get('location', '')
    room = request.args.get('room', '')
    summary = request.args.get('summary', '')
    room_price_number = request.args.get('roomPriceNumber', '')
    return render_template(
        'finalbookingform.html',
        resort=resort,
        checkin=checkin,
        checkout=checkout,
        location=location,
        room=room,
        summary=summary,
        roomPriceNumber=room_price_number
    )

@app.route('/emailtemplate.html', methods=['POST'])
def emailtemplate():
    guest_first_name = request.form.get('first_name', '')
    guest_last_name = request.form.get('last_name', '')
    smoking = request.form.get('smoking', '')
    bed = request.form.get('bed', '')
    resort_name = request.form.get('resort_name', '')
    checkin_date = request.form.get('checkin_date', '')
    checkout_date = request.form.get('checkout_date', '')
    nights = request.form.get('nights', '')
    room_type = request.form.get('room_type', '')
    guests = request.form.get('guests', '')
    special_requests = request.form.get('special_requests')
    if not special_requests:
        special_requests = f"Smoking: {smoking or 'None'}, Bed: {bed or 'None'}"
    payment_method = request.form.get('payment_method_real') or request.form.get('payment_method', '')
    total_amount = request.form.get('total_amount', '0')
    try:
        total_amount = float(total_amount)
    except Exception:
        total_amount = 0.0
    downpayment = round(total_amount * 0.15, 2)
    remaining_balance = round(total_amount - downpayment, 2)
    checkin_time = request.form.get('checkin_time', "2:00 PM")
    checkout_time = request.form.get('checkout_time', "12:00 PM")
    qr_codes = {
        "BlueWave Pool Resort": url_for('static', filename='images/QR/Gcash_BlueWave.jpg'),
        "AquaVibe Resort": url_for('static', filename='images/QR/Gcash_AquaVibe.jpg'),
        "CrystalSplash Poolside Haven": url_for('static', filename='images/QR/Gcash_CrystalSplash.jpg'),
        "Lagoon Cove Resort": url_for('static', filename='images/QR/Gcash_Lagoon.jpg'),
        "Sunset Waters Pool Resort": url_for('static', filename='images/QR/Gcash_Sunset Waters.jpg'),
        "CoolSprings Private Resort": url_for('static', filename='images/QR/Gcash_CoolSpring.jpg')
    }
    qr_path = qr_codes.get(resort_name) if payment_method and payment_method.lower() == "gcash" else None

    card_holder = request.form.get('card_holder', '')
    card_type = request.form.get('card_type', '')
    card_last4 = request.form.get('card_last4', '')
    card_reference = request.form.get('card_reference', '')
    card_amount_paid = request.form.get('card_amount_paid', downpayment)

    return render_template(
        'emailtemplate.html',
        guest_first_name=guest_first_name,
        guest_last_name=guest_last_name,
        resort_name=resort_name,
        checkin_date=checkin_date,
        checkin_time=checkin_time,
        checkout_date=checkout_date,
        checkout_time=checkout_time,
        nights=nights,
        room_type=room_type,
        guests=guests,
        special_requests=special_requests,
        payment_method=payment_method,
        total_amount=total_amount,
        downpayment=downpayment,
        remaining_balance=remaining_balance,
        qr_path=qr_path,
        current_year=datetime.now().year,
        card_holder=card_holder,
        card_type=card_type,
        card_last4=card_last4,
        card_reference=card_reference,
        card_amount_paid=card_amount_paid
    )

@app.route('/head_dashboard')
def head_dashboard():
    bookings = fetch_bookings()
    return render_template('head_dashboard.html', bookings=bookings, current_year=datetime.now().year)

@app.route('/aquavibe_dashboard.html')
def aquavibe_dashboard():
    bookings = fetch_bookings("AquaVibe Resort")
    bookings = [dict(row) for row in bookings]
    return render_template('aquavibe_dashboard.html', bookings=bookings, current_year=datetime.now().year)

@app.route('/bluewave_dashboard.html')
def bluewave_dashboard():
    bookings = fetch_bookings("BlueWave Pool Resort")
    return render_template('bluewave_dashboard.html', bookings=bookings, current_year=datetime.now().year)

@app.route('/coolsprings_dashboard.html')
def coolsprings_dashboard():
    bookings = fetch_bookings("CoolSprings Private Resort")
    return render_template('coolsprings_dashboard.html', bookings=bookings, current_year=datetime.now().year)

@app.route('/crystalsplash_dashboard.html')
def crystalsplash_dashboard():
    bookings = fetch_bookings("CrystalSplash Poolside Haven")
    return render_template('crystalsplash_dashboard.html', bookings=bookings, current_year=datetime.now().year)

@app.route('/lagoon_dashboard.html')
def lagoon_dashboard():
    bookings = fetch_bookings("Lagoon Cove Resort")
    return render_template('lagoon_dashboard.html', bookings=bookings, current_year=datetime.now().year)

@app.route('/sunset_dashboard.html')
def sunset_dashboard():
    bookings = fetch_bookings("Sunset Waters Pool Resort")
    return render_template('sunset_dashboard.html', bookings=bookings, current_year=datetime.now().year)

@app.route('/logout')
def logout():
    return redirect(url_for('head_dashboard')) 

@app.route('/feedback_dashboard')
def feedbacks_dashboard():
    feedbacks = get_all_feedbacks()
    return render_template('feedback_dashboard.html', feedbacks=feedbacks)

@app.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    resort_name = request.form['resort_name']
    guest_first_name = request.form['guest_first_name']
    guest_last_name = request.form['guest_last_name']
    checkin_date = request.form['checkin_date']
    checkin_time = request.form['checkin_time']
    checkout_date = request.form['checkout_date']
    checkout_time = request.form['checkout_time']
    nights = int(request.form['nights'])
    room_type = request.form['room_type']
    guests = request.form['guests']
    special_requests = request.form['special_requests']
    payment_method = request.form['payment_method']
    total_amount = float(request.form['total_amount'])
    downpayment = round(total_amount * 0.15, 2)
    remaining_balance = round(total_amount - downpayment, 2)
    status = request.form['status']
    qr_path = request.form['qr_path']
    reference_number = request.form.get('reference_number')
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Bank/Card info
    bank_number_last4 = request.form.get('card_last4', '')
    card_holder_name = request.form.get('card_holder', '')
    bank_reference_number = request.form.get('card_reference', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO admin_bookings (
            resort_name, guest_first_name, guest_last_name, checkin_date, checkin_time,
            checkout_date, checkout_time, nights, room_type, guests, special_requests,
            payment_method, total_amount, downpayment, remaining_balance, status, qr_path, reference_number,
            bank_number_last4, card_holder_name, bank_reference_number, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            resort_name, guest_first_name, guest_last_name, checkin_date, checkin_time,
            checkout_date, checkout_time, nights, room_type, guests, special_requests,
            payment_method, total_amount, downpayment, remaining_balance, status, qr_path, reference_number,
            bank_number_last4, card_holder_name, bank_reference_number, created_at
        )
    )
    conn.commit()
    conn.close()
    flash('Booking confirmed and saved!', 'success')
    return redirect(url_for('homepage'))

@app.route('/update_status/<int:booking_id>', methods=['POST'])
def update_status(booking_id):
    new_status = request.form.get('status')
    if new_status:
        conn = get_db_connection()
        conn.execute(
            'UPDATE admin_bookings SET status = ? WHERE id = ?',
            (new_status, booking_id)
        )
        conn.commit()
        conn.close()
        flash('Booking status updated!', 'success')
    else:
        flash('No status provided.', 'danger')
    return redirect(url_for('head_dashboard'))



if __name__ == '__main__':
    init_db()
    app.run(debug=True)
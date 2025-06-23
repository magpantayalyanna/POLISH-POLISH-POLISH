from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime, timedelta
import click
import os
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash, check_password_hash

from models.extensions import db
from models.models import Resort, Feedback, User, AdminBooking, TempBooking

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin_bookings.db'
app.secret_key = "your_secret_key"

db.init_app(app)

feedbacks = []

@click.command("init-db")
@with_appcontext
def init_db():
    db.create_all()
    
    resorts_data = [
        {"slug": "aquavibe-resort", "name": "AquaVibe Resort", "image_url": "static/images/Resort 1.jpg", "is_pet_friendly": False, "description": "Elegant pool resort with serene views."},
        {"slug": "crystalsplash-poolside-haven", "name": "CrystalSplash Poolside Haven", "image_url": "static/images/Resort 2.jpg", "is_pet_friendly": False, "description": "Modern poolside haven perfect for families."},
        {"slug": "sunset-waters-pool-resort", "name": "Sunset Waters Pool Resort", "image_url": "static/images/Resort 3.jpg", "is_pet_friendly": False, "description": "Experience unforgettable sunset swims."},
        {"slug": "bluewave-pool-resort", "name": "BlueWave Pool Resort", "image_url": "static/images/Resort 10.jpg", "is_pet_friendly": True, "description": "Pet-friendly resort with spacious pools."},
        {"slug": "lagoon-cove-resort", "name": "Lagoon Cove Resort", "image_url": "static/images/Resort 4.jpg", "is_pet_friendly": True, "description": "Relax in lush, pet-welcoming surroundings."},
        {"slug": "coolsprings-private-resort", "name": "CoolSprings Private Resort", "image_url": "static/images/Resort 6.jpg", "is_pet_friendly": True, "description": "Exclusive, pet-friendly private pools."}
    ]

    for resort_data in resorts_data:
        existing_resort = Resort.query.filter_by(slug=resort_data['slug']).first()
        if not existing_resort:
            new_resort = Resort(**resort_data)
            db.session.add(new_resort)

    db.session.commit()

    click.echo("Database initialized successfully with resorts populated.")

app.cli.add_command(init_db)

def fetch_bookings(resort_name=None):
    query = AdminBooking.query
    if resort_name:
        query = query.filter_by(resort_name=resort_name)
    bookings = query.order_by(AdminBooking.created_at.desc()).all()
    return bookings

def get_all_feedbacks():
    feedbacks = Feedback.query.order_by(Feedback.id.desc()).all()
    return feedbacks

@app.route('/', endpoint='homepage')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html')


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    resort_id = request.form.get('resort')
    message = request.form.get('message')

    if resort_id and message:
        # Check if the resort exists
        resort = Resort.query.get(resort_id)
        if not resort:
            flash("Selected resort does not exist.", "danger")
            return redirect(url_for('homepage'))

        # Save feedback
        feedback = Feedback(resort_id=resort_id, message=message)
        db.session.add(feedback)
        db.session.commit()

        flash("Thank you for your feedback!", "success")
    else:
        flash("Please select a resort and enter your feedback.", "danger")

    return redirect(url_for('homepage'))

@app.route('/2ndpage')
def explore():
    return render_template('2ndpage.html')

@app.route('/resorts')
def show_resorts():
    resorts = Resort.query.all()  # fetch all resorts via ORM
    return render_template('2ndpage.html', resorts=resorts)

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

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None  # Or redirect to login / handle anonymous users
    
    user = User.query.get(user_id)
    return user

@app.route('/finalbookingform.html')
def finalbookingform():
    # Booking info from URL params
    resort = request.args.get('resort', '')
    checkin = request.args.get('checkin', '')
    checkout = request.args.get('checkout', '')
    location = request.args.get('location', '')
    room = request.args.get('room', '')
    summary = request.args.get('summary', '')
    room_price_number = request.args.get('roomPriceNumber', '')
    user = get_current_user() 

    return render_template(
        'finalbookingform.html',
        resort=resort,
        checkin=checkin,
        checkout=checkout,
        location=location,
        room=room,
        summary=summary,
        roomPriceNumber=room_price_number,
        user = user
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
    downpayment = round(total_amount * 0.10, 2)
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


@app.route('/feedback_dashboard')
def feedbacks_dashboard():
    feedbacks = get_all_feedbacks()
    return render_template('feedback_dashboard.html', feedbacks=feedbacks)

@app.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    if 'user_id' not in session:
        flash('Please log in to confirm a booking.', 'danger')
        return redirect(url_for('login_page'))
    
    # Look up Resort by name (or use slug if better)
    resort = Resort.query.filter_by(name=request.form['resort_name']).first()
    if not resort:
        flash('Selected resort not found.', 'danger')
        return redirect(url_for('homepage'))
    
    resort_id = resort.id
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

    bank_number_last4 = request.form.get('card_last4', '')
    card_holder_name = request.form.get('card_holder', '')
    bank_reference_number = request.form.get('card_reference', '')

    resort = Resort.query.get(resort_id)
    if not resort:
        flash('Selected resort not found.', 'danger')
        return redirect(url_for('homepage'))

    booking = AdminBooking(
        resort_id=resort_id,
        user_id=session['user_id'],
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
        status=status,
        qr_path=qr_path,
        reference_number=reference_number,
        bank_number_last4=bank_number_last4,
        card_holder_name=card_holder_name,
        bank_reference_number=bank_reference_number,
        created_at=created_at
    )

    db.session.add(booking)
    db.session.commit()

    flash('Booking confirmed and saved!', 'success')
    return redirect(url_for('homepage'))

@app.route('/update_status/<int:booking_id>', methods=['POST'])
def update_status(booking_id):
    new_status = request.form.get('status')

    if new_status:
        # Fetch booking by id
        booking = AdminBooking.query.get(booking_id)
        if booking:
            booking.status = new_status
            db.session.commit()
            flash('Booking status updated!', 'success')
        else:
            flash('Booking not found.', 'danger')
    else:
        flash('No status provided.', 'danger')

    return redirect(url_for('head_dashboard'))

@app.route('/get-booked-dates')
def get_booked_dates():
    # Fetch bookings with status not 'Cancelled'
    bookings = AdminBooking.query.filter(AdminBooking.status != 'Cancelled').all()

    disabled_dates = []

    for booking in bookings:
        start = datetime.strptime(booking.checkin_date, '%Y-%m-%d')
        end = datetime.strptime(booking.checkout_date, '%Y-%m-%d')
        delta = end - start

        for i in range(delta.days + 1):
            day = start + timedelta(days=i)
            disabled_dates.append(day.strftime('%Y-%m-%d'))

    return jsonify(disabled_dates)


@app.route('/signup', methods=['POST'])
def signup():
    full_name = request.form['full_name']
    email = request.form['email']
    password = request.form['password']
    contact_number = request.form['contact_number']

    # Check if email is already registered
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already registered.', 'danger')
        return redirect(url_for('login'))

    # Hash password securely
    hashed_password = generate_password_hash(password)

    # Create new user record
    new_user = User(
        username=email,  # using email as username
        password=hashed_password,
        full_name=full_name,
        email=email,
        contact_number=contact_number
    )

    db.session.add(new_user)
    db.session.commit()

    flash('Signup successful, please login.', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')  # your login page template

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Find user by email
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['user_name'] = user.full_name
        flash('Login successful!', 'success')
        return redirect(url_for('show_resorts'))
    else:
        flash('Invalid email or password.', 'danger')
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
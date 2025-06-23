from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime, timedelta
import click
import os
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash, check_password_hash

from models.extensions import db
from models.models import Resort, Feedback, Room, User, AdminBooking, TempBooking

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin_bookings.db'
app.secret_key = "your_secret_key"

db.init_app(app)

feedbacks = []

@click.command("init-db")
@with_appcontext
def init_db():
    db.drop_all()
    db.create_all()
    
    # Extended resort data with location, maps, and amenities
    resorts_data = [
        {
            "slug": "bluewave-pool-resort",
            "name": "BlueWave Pool Resort",
            "image_url": "static/images/Resort 10.jpg",
            "is_pet_friendly": True,
            "description": "Enjoy a relaxing stay at BlueWave, featuring spacious pools and family-friendly amenities.",
            "location": "Lipa, Batangas",
            "google_maps_link": "https://www.google.com/maps?q=Lipa,+Batangas",
            "amenities": ["Wave pool", "Cottages", "Grill area", "Kiddie pool"]
        },
        {
            "slug": "aquavibe-resort",
            "name": "AquaVibe Resort",
            "image_url": "static/images/Resort 1.jpg",
            "is_pet_friendly": False,
            "description": "AquaVibe is the perfect getaway for groups and barkadas, with vibrant pools and party amenities.",
            "location": "San Juan, Batangas",
            "google_maps_link": "https://bit.ly/3HQMwoQ",
            "amenities": ["Infinity pool", "Function hall", "Music lounge", "Picnic area"]
        },
        {
            "slug": "crystalsplash-poolside-haven",
            "name": "CrystalSplash Poolside Haven",
            "image_url": "static/images/Resort 2.jpg",
            "is_pet_friendly": False,
            "description": "CrystalSplash offers elegant poolside relaxation, perfect for weekend family escapes.",
            "location": "Nasugbu, Batangas",
            "google_maps_link": "bit.ly/4eijVVG",
            "amenities": ["Lap pool", "Gazebos", "Jacuzzi", "Private suites"]
        },
        {
            "slug": "lagoon-cove-resort",
            "name": "Lagoon Cove Resort",
            "image_url": "static/images/Resort 4.jpg",
            "is_pet_friendly": True,
            "description": "A nature-inspired pool resort with a relaxing lagoon, perfect for unwinding and reunions.",
            "location": "Tanauan, Batangas",
            "google_maps_link": "https://www.google.com/maps?q=Tanauan,+Batangas",
            "amenities": ["Lagoon pool", "BBQ pit", "Wide lawn", "Clubhouse"]
        },
        {
            "slug": "sunset-waters-pool-resort",
            "name": "Sunset Waters Pool Resort",
            "image_url": "static/images/Resort 3.jpg",
            "is_pet_friendly": False,
            "description": "Enjoy beautiful sunset views and a relaxing pool experience at Sunset Waters Pool Resort.",
            "location": "Balayan, Batangas",
            "google_maps_link": "https://www.google.com/maps?q=Balayan,+Batangas",
            "amenities": ["Sunset deck", "Adult and kiddie pools", "Open cabanas", "Bar & grill"]
        },
        {
            "slug": "coolsprings-private-resort",
            "name": "CoolSprings Private Resort",
            "image_url": "static/images/Resort 6.jpg",
            "is_pet_friendly": True,
            "description": "Experience exclusive privacy and cool spring water pools, ideal for private gatherings.",
            "location": "Sto. Tomas, Batangas",
            "google_maps_link": "https://www.google.com/maps?q=Sto.+Tomas,+Batangas",
            "amenities": ["Private pool villas", "Natural spring water", "Conference room", "Bonfire area"]
        }
    ]

    # Room data for each resort
    rooms_data = {
        "bluewave-pool-resort": [
            {
                "room_name": "Garden Room",
                "price": 4000,
                "capacity_min": 2,
                "capacity_max": 3,
                "description": "Cozy room with garden views, queen-size bed, and breakfast.",
                "image_url": "static/images/Garden Type 1.jpg",
                "amenities": ["Queen-size bed", "Garden view", "Complimentary breakfast"]
            },
            {
                "room_name": "Beachfront Suite",
                "price": 7000,
                "capacity_min": 2,
                "capacity_max": 6,
                "description": "Suites directly facing the sea, king-size bed, balcony.",
                "image_url": "static/images/Beach Front 1.jpg",
                "amenities": ["King-size bed", "Balcony with sea view", "Direct beach access"]
            }
        ],
        "aquavibe-resort": [
            {
                "room_name": "Mountain View Room",
                "price": 5500,
                "capacity_min": 2,
                "capacity_max": 3,
                "description": "Rooms overlooking lush mountains, twin beds.",
                "image_url": "static/images/Garden Type 2.jpg",
                "amenities": ["Twin beds", "Mountain view"]
            },
            {
                "room_name": "Lagoon Suite",
                "price": 8200,
                "capacity_min": 2,
                "capacity_max": 6,
                "description": "Spacious suite with lagoon access, living room.",
                "image_url": "static/images/Beach Front 2.jpg",
                "amenities": ["Lagoon access", "Living room"]
            }
        ],
        "crystalsplash-poolside-haven": [
            {
                "room_name": "Deluxe Room",
                "price": 6000,
                "capacity_min": 2,
                "capacity_max": 3,
                "description": "Modern room with pool access and breakfast.",
                "image_url": "static/images/Garden Type 3.jpg",
                "amenities": ["Pool access", "Complimentary breakfast"]
            },
            {
                "room_name": "Infinity Suite",
                "price": 10000,
                "capacity_min": 2,
                "capacity_max": 6,
                "description": "Suite with infinity pool views, luxurious amenities.",
                "image_url": "static/images/Beach Front 3.jpg",
                "amenities": ["Infinity pool view", "Luxury amenities"]
            }
        ],
        "lagoon-cove-resort": [
            {
                "room_name": "Superior Room",
                "price": 5200,
                "capacity_min": 2,
                "capacity_max": 3,
                "description": "Spacious room with pool or garden view, twin beds.",
                "image_url": "static/images/Garden Type 4.jpg",
                "amenities": ["Twin beds", "Pool/garden view"]
            },
            {
                "room_name": "Family Suite",
                "price": 8800,
                "capacity_min": 4,
                "capacity_max": 6,
                "description": "Large suite for families, 2 bedrooms, living area.",
                "image_url": "static/images/Beach Front 4.jpg",
                "amenities": ["2 Bedrooms", "Living area"]
            }
        ],
        "sunset-waters-pool-resort": [
            {
                "room_name": "Standard Room",
                "price": 4800,
                "capacity_min": 2,
                "capacity_max": 3,
                "description": "Comfortable room with twin beds, basic amenities.",
                "image_url": "static/images/Garden Type 5.jpg",
                "amenities": ["Twin beds", "Air conditioning"]
            },
            {
                "room_name": "Deluxe Suite",
                "price": 7200,
                "capacity_min": 2,
                "capacity_max": 6,
                "description": "Spacious suite, sea view, king-sized bed.",
                "image_url": "static/images/Beach Front 5.jpg",
                "amenities": ["Sea view", "King-sized bed"]
            }
        ],
        "coolsprings-private-resort": [
            {
                "room_name": "Sulu Terrace",
                "price": 9000,
                "capacity_min": 2,
                "capacity_max": 3,
                "description": "Rustic Filipino-inspired villa, garden view, queen-size bed.",
                "image_url": "static/images/Garden Type 6.jpg",
                "amenities": ["Garden view", "Queen-size bed"]
            },
            {
                "room_name": "Narra Pool Villa",
                "price": 18000,
                "capacity_min": 2,
                "capacity_max": 6,
                "description": "Private villa with pool, luxurious amenities, forest view.",
                "image_url": "static/images/Beach Front 6.png",
                "amenities": ["Private pool", "Forest view"]
            }
        ]
    }

    # Insert resorts
    for resort_data in resorts_data:
        existing_resort = Resort.query.filter_by(slug=resort_data['slug']).first()
        if not existing_resort:
            new_resort = Resort(**resort_data)
            db.session.add(new_resort)
            db.session.flush()  # Flush to get the resort in the session
            
            # Insert rooms for this resort
            resort_slug = resort_data['slug']
            if resort_slug in rooms_data:
                for room_data in rooms_data[resort_slug]:
                    room_data['resort_slug'] = resort_slug
                    new_room = Room(**room_data)
                    db.session.add(new_room)

    db.session.commit()
    click.echo("Database initialized successfully with resorts and rooms populated.")

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
    resort_slug = request.args.get('resort')
    
    # Get resort information
    resort = Resort.query.filter_by(slug=resort_slug).first()
    
    if not resort:
        return render_template('3rdpage.html', resort=None, resort_data=None, rooms=[], feedbacks=[])
    
    # Get rooms for this resort
    rooms = Room.query.filter_by(resort_slug=resort_slug).all()
    
    # Get feedbacks for this resort
    all_feedbacks = get_all_feedbacks()
    feedbacks = []
    for fb in all_feedbacks:
        if fb['resort_name'] == resort_slug:
            feedbacks.append({'resort': fb['resort_name'], 'message': fb['message']})
    
    # Prepare resort data
    resort_data = {
        'slug': resort.slug,
        'name': resort.name,
        'description': resort.description,
        'location': resort.location,
        'google_maps_link': resort.google_maps_link,
        'amenities': resort.amenities or [],
        'image_url': resort.image_url,
        'id': resort.id,
    }
    
    # Prepare rooms data
    rooms_data = []
    for room in rooms:
        rooms_data.append({
            'id': room.id,
            'room_name': room.room_name,
            'price': room.price,
            'capacity_min': room.capacity_min,
            'capacity_max': room.capacity_max,
            'description': room.description,
            'image_url': room.image_url,
            'amenities': room.amenities or [],
            'total_slots': room.total_slots
        })
    
    return render_template('3rdpage.html', 
                         resort=resort_slug, 
                         resort_data=resort_data, 
                         rooms=rooms_data, 
                         feedbacks=feedbacks)

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
    
    # Get resort by name (or use slug if better)
    resort = Resort.query.filter_by(name=request.form['resort_name']).first()
    if not resort:
        flash('Selected resort not found.', 'danger')
        return redirect(url_for('homepage'))
    
    resort_id = resort.id

    # Get room by name/type and resort_id
    room_type = request.form['room_type']
    room = Room.query.filter_by(room_name=room_type, resort_slug=resort.slug).first()
    if not room:
        flash('Selected room type not found.', 'danger')
        return redirect(url_for('homepage'))

    room_id = room.id

    # Booking details
    checkin_date = request.form['checkin_date']
    checkin_time = request.form['checkin_time']
    checkout_date = request.form['checkout_date']
    checkout_time = request.form['checkout_time']
    nights = int(request.form['nights'])
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

    # Create booking
    booking = AdminBooking(
        resort_id=resort_id,
        room_id=room_id,
        user_id=session['user_id'],
        checkin_date=checkin_date,
        checkin_time=checkin_time,
        checkout_date=checkout_date,
        checkout_time=checkout_time,
        nights=nights,
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
    bookings = AdminBooking.query.filter(AdminBooking.status != 'Cancelled').all()

    disabled_dates = {}

    for booking in bookings:
        resort_id = booking.resort_id
        room_id = booking.room_id  # Assuming you now have a room_id field in AdminBooking

        if resort_id not in disabled_dates:
            disabled_dates[resort_id] = {}

        if room_id not in disabled_dates[resort_id]:
            disabled_dates[resort_id][room_id] = []

        start = datetime.strptime(booking.checkin_date, '%Y-%m-%d')
        end = datetime.strptime(booking.checkout_date, '%Y-%m-%d')
        delta = end - start

        for i in range(delta.days + 1):
            day = start + timedelta(days=i)
            date_str = day.strftime('%Y-%m-%d')

            if date_str not in disabled_dates[resort_id][room_id]:
                disabled_dates[resort_id][room_id].append(date_str)

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
from collections import defaultdict
from operator import and_
from flask import Flask, abort, json, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import date, datetime, timedelta
import click
import os
from flask.cli import with_appcontext
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

from models.extensions import db
from models.models import Resort, Feedback, Room, AdminBooking

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
    query = db.session.query(
        AdminBooking,
        Resort.name.label('resort_name'),
        Room.room_name.label('room_type')
    ).join(Resort, AdminBooking.resort_id == Resort.id
    ).join(Room, AdminBooking.room_id == Room.id)

    if resort_name:
        query = query.filter(Resort.name == resort_name)

    query = query.order_by(AdminBooking.created_at.desc())
    results = query.all()

    # Build list of dicts for template
    bookings = []
    for booking, resort_name, room_type in results:
        bookings.append({
            'id': booking.id,
            'resort_name': resort_name,
            'guest_first_name': booking.guest_first_name,
            'guest_last_name': booking.guest_last_name,
            'checkin_date': booking.checkin_date,
            'checkout_time': '',  # if you plan to add time later
            'checkout_date': booking.checkout_date,
            'checkin_time': '',  # if you plan to add time later
            'room_type': room_type,
            'guests': booking.guests,
            'payment_method': booking.payment_method,
            'total_amount': booking.total_amount,
            'downpayment': booking.downpayment,
            'remaining_balance': booking.remaining_balance,
            'reference_number': booking.reference_number,
            'status': booking.status,
            'bank_number_last4': booking.bank_number_last4,
            'card_holder_name': booking.card_holder_name,
            'guest_phone': booking.guest_phone,
            'guest_email': booking.guest_email,
        })

    return bookings



def get_all_feedbacks():
    feedbacks = Feedback.query.order_by(Feedback.id.desc()).all()
    return feedbacks

@app.route('/', endpoint='homepage')
def dashboard():
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
    numberOfRooms = request.args.get('numberOfRooms', '1')

    return render_template(
        'finalbookingform.html',
        resort=resort,
        checkin=checkin,
        checkout=checkout,
        location=location,
        room=room,
        summary=summary,
        roomPriceNumber=room_price_number,
        numberOfRooms=numberOfRooms,
    )


@app.route('/emailtemplate.html', methods=['POST'])
def emailtemplate():
    guest_first_name = request.form.get('first_name', '')
    guest_last_name = request.form.get('last_name', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    smoking = request.form.get('smoking', '')
    bed = request.form.get('bed', '')
    resort_name = request.form.get('resort_name', '')
    checkin_date = request.form.get('checkin_date', '')
    checkout_date = request.form.get('checkout_date', '')
    nights = request.form.get('nights', '')
    room_type = request.form.get('room_type', '')
    guests = request.form.get('guests', '')
    numberOfRooms = request.form.get('numberOfRooms', '1')
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
        card_amount_paid=card_amount_paid,
        email=email,
        phone=phone,
        numberOfRooms=numberOfRooms
    )

@app.route('/head_dashboard')
def head_dashboard():
    # Get all resorts and their rooms
    resort_rooms = {}
    
    for key, name in RESORT_MAPPING.items():
        resort = Resort.query.filter_by(name=name).first()
        if resort:
            rooms = Room.query.filter_by(resort_slug=resort.slug).all()
            resort_rooms[key] = rooms
        else:
            resort_rooms[key] = []
    bookings = fetch_bookings()
    return render_template('head_dashboard.html', 
                         resort_rooms=resort_rooms,
                         current_year=datetime.now().year,
                         bookings=bookings) 

@app.route('/update_room_slots', methods=['POST'])
def update_room_slots():
    try:
        data = request.get_json()
        room_id = data.get('room_id')
        change = data.get('change', 0)
        
        room = Room.query.get(room_id)
        if not room:
            return jsonify({'success': False, 'error': 'Room not found'}), 404

        new_total = room.total_slots + change
        if new_total < 0:
            return jsonify({'success': False, 'error': 'Cannot have negative slots'}), 400

        if change < 0:
            today = date.today()
            confirmed_bookings = AdminBooking.query.filter(
                AdminBooking.room_id == room.id,
                AdminBooking.status == 'confirmed',
                AdminBooking.checkout_date >= str(today)
            ).all()

            if len(confirmed_bookings) > new_total:
                return jsonify({
                    'success': False, 
                    'error': f'Cannot reduce slots. There are {len(confirmed_bookings)} active bookings.'
                }), 400

        room.total_slots = new_total
        db.session.commit()

        return jsonify({
            'success': True, 
            'new_total': room.total_slots,
            'room_id': room.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def prepare_calendar_events(bookings):
    """Prepare calendar events with color coding and extended details for tooltip."""
    events = []
    for booking in bookings:
        status = booking.get('status', '').lower()

        # Color coding based on status
        if status == 'confirmed':
            color = "#38a169"
        elif status == 'pending':
            color = "#ecc94b"
        else:
            color = "#e53e3e"

        print(booking)
        # Prepare event object
        events.append({
            "title": f"{booking['guest_first_name']} {booking['guest_last_name']} ({booking['status']})",
            "start": booking['checkin_date'],
            "end": booking['checkout_date'],
            "color": color,
            "extendedProps": {
                "guest_name": f"{booking['guest_first_name']} {booking['guest_last_name']}",
                "guest_email": booking.get('guest_email'),
                "guest_phone": booking.get('guest_phone'),
                "details":booking.get('guests'),
                "num_rooms": booking.get('num_rooms'),
                "payment_method": booking.get('payment_method'),
                "total_amount": booking.get('total_amount'),
                "special_requests": booking.get('special_requests'),
                "reference_number": booking.get('reference_number'),
                "notes": booking.get('notes')
            }
        })
    return events


# Define resort mapping
RESORT_MAPPING = {
    'bluewave': 'BlueWave Pool Resort',
    'coolsprings': 'CoolSprings Private Resort',
    'crystalsplash': 'CrystalSplash Poolside Haven',
    'lagoon': 'Lagoon Cove Resort',
    'sunset': 'Sunset Waters Pool Resort',
    'aquavibe': 'AquaVibe Resort'
}
# Updated resort dashboard route
@app.route('/<resort_key>_dashboard.html')
def resort_dashboard(resort_key):
    # Exclude head_dashboard
    if resort_key == 'head':
        abort(404)
    
    # Get the full resort name from the mapping
    resort_name = RESORT_MAPPING.get(resort_key)
    
    if not resort_name:
        abort(404)  # Resort not found
    
    # Get date from query parameter if provided
    selected_date = request.args.get('date', None)
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    bookings = fetch_bookings(resort_name)
    events = prepare_calendar_events(bookings)
    room_availability = calculate_room_availability(resort_name, selected_date)
    return render_template('resort_dashboard.html', 
                         bookings=bookings,
                         resort_name=resort_name,
                         calendar_events=json.dumps(events),
                         room_availability=room_availability,
                         selected_date=selected_date.strftime('%Y-%m-%d'),
                         current_year=datetime.now().year)


def calculate_room_availability(resort_name, target_date=None):
    if target_date is None:
        target_date = date.today()

    # Get the resort slug from the resort name
    resort = Resort.query.filter_by(name=resort_name).first()
    if not resort:
        return {}

    # Get all rooms for this resort
    rooms = Room.query.filter_by(resort_slug=resort.slug).all()

    # Map room_id to room_name and store room info
    room_info = {}
    room_id_to_name = {}
    for room in rooms:
        room_info[room.room_name] = {
            'room_id': room.id,
            'total_slots': room.total_slots,
            'price': room.price,
            'capacity': f"{room.capacity_min}-{room.capacity_max}",
            'is_booking': room.is_booking
        }
        room_id_to_name[room.id] = room.room_name

    room_ids = [room.id for room in rooms]

    # Get confirmed bookings for the target date and resort
    confirmed_bookings = AdminBooking.query.filter(
        AdminBooking.room_id.in_(room_ids),
        AdminBooking.status == 'confirmed',
        AdminBooking.checkin_date <= target_date.strftime('%Y-%m-%d'),
        AdminBooking.checkout_date > target_date.strftime('%Y-%m-%d')
    ).all()

    # Count occupied slots per room_id (accounting for num_rooms booked)
    room_occupied = defaultdict(int)
    for booking in confirmed_bookings:
        room_occupied[booking.room_id] += booking.num_rooms

    # Calculate availability per room_name
    room_availability = {}
    for room_name, info in room_info.items():
        occupied = room_occupied.get(info['room_id'], 0)
        available = info['total_slots'] - occupied

        room_availability[room_name] = {
            'total': info['total_slots'],
            'occupied': occupied,
            'available': available,
            'price': info['price'],
            'capacity': info['capacity'],
            'is_booking': info['is_booking'],
            'occupancy_rate': round((occupied / info['total_slots'] * 100), 1) if info['total_slots'] > 0 else 0
        }

    print(f"Room availability for {resort_name} on {target_date}: {room_availability}")
    return room_availability

@app.route('/feedback_dashboard')
def feedbacks_dashboard():
    feedbacks = get_all_feedbacks()
    return render_template('feedback_dashboard.html', feedbacks=feedbacks)

@app.route('/confirm-booking', methods=['POST'])
def confirm_booking():
    
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
    checkin_date = datetime.strptime(request.form['checkin_date'], '%Y-%m-%d').date()
    checkout_date = datetime.strptime(request.form['checkout_date'], '%Y-%m-%d').date()
    nights = int(request.form['nights'])
    guests = request.form['guests']
    special_requests = request.form['special_requests']
    payment_method = request.form['payment_method']
    total_amount = float(request.form['total_amount'])
    downpayment = round(total_amount * 0.15, 2)
    remaining_balance = round(total_amount - downpayment, 2)
    status = 'pending'
    qr_path = request.form['qr_path']
    reference_number = request.form.get('reference_number')
    created_at = datetime.now()

    bank_number_last4 = request.form.get('card_last4', '')
    card_holder_name = request.form.get('card_holder', '')
    bank_reference_number = request.form.get('card_reference', '')

    guest_first_name = request.form.get('guest_first_name', '')
    guest_last_name = request.form.get('guest_last_name', '')
    guest_email = request.form.get('email', '')
    guest_phone = request.form.get('phone', '')
    num_rooms = request.form.get('numberOfRooms', 1)

    # Create booking
    booking = AdminBooking(
        resort_id=resort_id,
        room_id=room_id,
        checkin_date=checkin_date,
        checkout_date=checkout_date,
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
        created_at=created_at,
        guest_first_name=guest_first_name,
        guest_last_name=guest_last_name,
        guest_email=guest_email,
        guest_phone=guest_phone,
        num_rooms=num_rooms
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

@app.route('/get-room-data')
def get_room_data():
    rooms = Room.query.all()

    room_data = {}
    for room in rooms:
        room_data[room.id] = {
            'room_name': room.room_name,
            'price': room.price,
            'capacity_min': room.capacity_min,
            'capacity_max': room.capacity_max,
            'description': room.description,
            'image_url': room.image_url,
            'total_slots': room.total_slots,
            'resort_slug': room.resort_slug
        }

    return jsonify(room_data)


@app.route('/get-booked-dates')
def get_booked_dates():
    room_id = request.args.get('room_id')

    if not room_id:
        return jsonify({'error': 'Missing room_id'}), 400

    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    total_slots = room.total_slots

    # Fetch bookings only for this room
    bookings = AdminBooking.query.filter_by(room_id=room_id).all()

    bookings_per_day = {}
    disabled = []

    for booking in bookings:
        start = datetime.strptime(booking.checkin_date, '%Y-%m-%d')
        end = datetime.strptime(booking.checkout_date, '%Y-%m-%d')
        num_rooms = getattr(booking, 'num_rooms', 1) or 1  # fallback if null/None

        while start < end:
            date_str = start.strftime('%Y-%m-%d')
            bookings_per_day[date_str] = bookings_per_day.get(date_str, 0) + num_rooms
            if bookings_per_day[date_str] >= total_slots:
                if date_str not in disabled:
                    disabled.append(date_str)
            start += timedelta(days=1)

    return jsonify({
        'disabled': disabled,
        'bookings_per_day': bookings_per_day,
        'total_slots': total_slots
    })

from datetime import datetime, date, timedelta

@app.route('/get-room-slots')
def get_room_slots():
    room_id = request.args.get('room_id')
    if not room_id:
        return jsonify({'error': 'Missing room_id'}), 400

    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    total_slots = room.total_slots
    bookings = AdminBooking.query.filter_by(room_id=room_id).all()

    bookings_per_day = {}

    # Count bookings per day based on actual booking dates
    for booking in bookings:
        start = datetime.strptime(booking.checkin_date, '%Y-%m-%d').date()
        end = datetime.strptime(booking.checkout_date, '%Y-%m-%d').date()
        num_rooms = booking.num_rooms or 1

        while start < end:
            date_str = start.strftime('%Y-%m-%d')
            bookings_per_day[date_str] = bookings_per_day.get(date_str, 0) + num_rooms
            start += timedelta(days=1)

    # Now compute available slots per day for the next 1 year
    available_slots_per_day = {}
    today = date.today()
    one_year_later = today + timedelta(days=365)
    current_day = today

    while current_day <= one_year_later:
        date_str = current_day.strftime('%Y-%m-%d')
        booked = bookings_per_day.get(date_str, 0)
        remaining = max(0, total_slots - booked)
        available_slots_per_day[date_str] = remaining
        current_day += timedelta(days=1)

    return jsonify({
        'totalSlots': total_slots,
        'bookingsPerDay': bookings_per_day,
        'availableSlotsPerDay': available_slots_per_day
    })

@app.route('/set_room_booking_status', methods=['POST'])
def set_room_booking_status_api():
    data = request.get_json()

    room_id = data.get('room_id')
    status = data.get('status')

    room = Room.query.get(room_id)
    if not room:
        return jsonify({'success': False, 'message': 'Room not found.'}), 404

    room.is_booking = 1 if status else 0
    db.session.commit()

    return jsonify({'success': True, 'message': f'Room {room_id} booking status set to {status}.'})

@app.route('/check_room_booking_status', methods=['GET'])
def check_room_booking_status():
    room_id = request.args.get('room_id')
    if not room_id:
        return jsonify({'success': False, 'message': 'Missing room_id'}), 400

    room = Room.query.get(room_id)
    if not room:
        return jsonify({'success': False, 'message': 'Room not found'}), 404

    return jsonify({'success': True, 'is_booking': room.is_booking})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
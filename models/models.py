from datetime import datetime
from models.extensions import db

class Resort(db.Model):
    __tablename__ = 'resorts'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, unique=True, nullable=False)  # This is resort_id in our design
    name = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    is_pet_friendly = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    location = db.Column(db.String)
    google_maps_link = db.Column(db.String)
    amenities = db.Column(db.JSON)
    
    # Relationship to rooms
    rooms = db.relationship('Room', backref='resort', lazy=True, cascade='all, delete-orphan')


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    resort_slug = db.Column(db.String, db.ForeignKey('resorts.slug'), nullable=False)
    room_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    capacity_min = db.Column(db.Integer, nullable=False)
    capacity_max = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    amenities = db.Column(db.JSON)
    total_slots = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_booking = db.Column(db.Integer, default=0)

class AdminBooking(db.Model):
    __tablename__ = 'admin_bookings'

    id = db.Column(db.Integer, primary_key=True)
    resort_id = db.Column(db.Integer, db.ForeignKey('resorts.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    guest_first_name = db.Column(db.String, nullable=False)
    guest_last_name = db.Column(db.String, nullable=False)
    guest_email = db.Column(db.String, nullable=False)
    guest_phone = db.Column(db.String, nullable=False)
    
    checkin_date = db.Column(db.String, nullable=False)
    checkout_date = db.Column(db.String, nullable=False)
    nights = db.Column(db.Integer)
    num_rooms = db.Column(db.Integer, nullable=False, default=1)  # ← new column for number of rooms booked
    
    guests = db.Column(db.String)
    special_requests = db.Column(db.Text)
    payment_method = db.Column(db.String)
    total_amount = db.Column(db.Float)
    downpayment = db.Column(db.Float)
    remaining_balance = db.Column(db.Float)
    status = db.Column(db.String)
    qr_path = db.Column(db.String)
    reference_number = db.Column(db.String)
    bank_number_last4 = db.Column(db.String)
    card_holder_name = db.Column(db.String)
    bank_reference_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resort = db.relationship('Resort', backref=db.backref('bookings', lazy=True))
    room = db.relationship('Room', backref=db.backref('bookings', lazy=True))


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    resort_id = db.Column(db.Integer, db.ForeignKey('resorts.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)

    # Optional: relationship if you want to access resort details easily
    resort = db.relationship('Resort', backref=db.backref('feedbacks', lazy=True))
from models.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    contact_number = db.Column(db.String)


class Resort(db.Model):
    __tablename__ = 'resorts'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    is_pet_friendly = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)


class AdminBooking(db.Model):
    __tablename__ = 'admin_bookings'

    id = db.Column(db.Integer, primary_key=True)
    resort_id = db.Column(db.Integer, db.ForeignKey('resorts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    checkin_date = db.Column(db.String)
    checkin_time = db.Column(db.String)
    checkout_date = db.Column(db.String)
    checkout_time = db.Column(db.String)
    nights = db.Column(db.Integer)
    room_type = db.Column(db.String)
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
    created_at = db.Column(db.String)
    is_booking = db.Column(db.Integer, default=0)

    # Optional relationships for easier joins/access
    resort = db.relationship('Resort', backref=db.backref('bookings', lazy=True))
    user = db.relationship('User', backref=db.backref('bookings', lazy=True))


class TempBooking(db.Model):
    __tablename__ = 'temp_bookings'

    id = db.Column(db.Integer, primary_key=True)
    resort_name = db.Column(db.String)
    checkin_date = db.Column(db.String)
    checkin_time = db.Column(db.String)
    checkout_date = db.Column(db.String)
    checkout_time = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    resort_id = db.Column(db.Integer, db.ForeignKey('resorts.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)

    # Optional: relationship if you want to access resort details easily
    resort = db.relationship('Resort', backref=db.backref('feedbacks', lazy=True))
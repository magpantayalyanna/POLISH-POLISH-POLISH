import sqlite3

conn = sqlite3.connect('admin_bookings.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS admin_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resort_name TEXT NOT NULL,
    guest_first_name TEXT NOT NULL,
    guest_last_name TEXT NOT NULL,
    checkin_date TEXT NOT NULL,
    checkin_time TEXT NOT NULL,
    checkout_date TEXT NOT NULL,
    checkout_time TEXT NOT NULL,
    nights INTEGER NOT NULL,
    room_type TEXT NOT NULL,
    guests TEXT NOT NULL,
    special_requests TEXT,
    payment_method TEXT NOT NULL, 
    total_amount REAL NOT NULL,
    downpayment REAL,          -- Added downpayment column
    remaining_balance REAL,    -- Added remaining_balance column
    status TEXT NOT NULL,
    qr_path TEXT,
    created_at TEXT DEFAULT (datetime('now','localtime'))
)
''') 

# New bank_payments table
c.execute('''
CREATE TABLE IF NOT EXISTS bank_payments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    bank_number_last4 TEXT NOT NULL,
    card_holder_name TEXT NOT NULL,
    reference_number TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (booking_id) REFERENCES admin_bookings(id)
)
''') 

conn.commit()
conn.close()
print("admin_bookings table created in admin_bookings.db!")
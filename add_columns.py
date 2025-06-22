import sqlite3

conn = sqlite3.connect('admin_bookings.db')
c = conn.cursor()

# Add columns only if they do not exist (sqlite doesn't support IF NOT EXISTS for columns, so you need to try/except)
try:
    c.execute('ALTER TABLE admin_bookings ADD COLUMN downpayment REAL')
except sqlite3.OperationalError:
    print("Column 'downpayment' already exists.")

try:
    c.execute('ALTER TABLE admin_bookings ADD COLUMN remaining_balance REAL')
except sqlite3.OperationalError:
    print("Column 'remaining_balance' already exists.")

conn.commit()
conn.close()
print("Columns added if they did not exist.")
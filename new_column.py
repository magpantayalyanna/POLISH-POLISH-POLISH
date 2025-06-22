import sqlite3

conn = sqlite3.connect('admin_bookings.db')
c = conn.cursor()

# Add the new column 'reference_number' if it does not exist
try:
    c.execute('ALTER TABLE admin_bookings ADD COLUMN reference_number TEXT')
    print("Column 'reference_number' added to admin_bookings table!")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column 'reference_number' already exists in admin_bookings table.")
    else:
        raise

conn.commit()
conn.close()
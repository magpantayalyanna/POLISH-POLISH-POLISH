import sqlite3

conn = sqlite3.connect('admin_bookings.db')
c = conn.cursor()

# Add new columns for bank/card info only if they don't already exist
def add_column_if_not_exists(cursor, table, column, col_type):
    # Check if the column already exists
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor.fetchall()]
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        print(f"Added column: {column} ({col_type})")
    else:
        print(f"Column already exists: {column}")

add_column_if_not_exists(c, 'admin_bookings', 'bank_number_last4', 'TEXT')
add_column_if_not_exists(c, 'admin_bookings', 'card_holder_name', 'TEXT')
add_column_if_not_exists(c, 'admin_bookings', 'bank_reference_number', 'TEXT')

conn.commit()
conn.close()
print("ALTER TABLE admin_bookings: Bank/card columns ensured.")
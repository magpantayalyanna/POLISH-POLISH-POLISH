import sqlite3

# Connect to SQLite database (creates feedback.db if it doesn't exist)
conn = sqlite3.connect('feedback.db')

# Create a table for feedback
conn.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resort_name TEXT NOT NULL,
    message TEXT NOT NULL
)
''')

print("✅ Database and table created successfully.")

conn.commit()
conn.close()
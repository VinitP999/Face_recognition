import sqlite3

# Connect to database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Insert default admin user
admin_username = "admin"
admin_password = "admin123"  # Change this if needed

cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (admin_username, admin_password))

# Save and close
conn.commit()
conn.close()

print("✅ Database setup complete! Default Admin Login: admin / admin123")

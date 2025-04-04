import sqlite3

# ✅ Ensure the database and table exist
def initialize_db():
    conn = sqlite3.connect("patients.db")
    cursor = conn.cursor()

    # ✅ Drop the old table (only if you manually run this ONCE to fix the structure)
    cursor.execute("DROP TABLE IF EXISTS patients")

    # ✅ Recreate the correct table with the `condition` column
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            condition TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# ✅ Fix: Correct `save_patient` function
def save_patient(name, age, condition):
    conn = sqlite3.connect("patients.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO patients (name, age, condition) VALUES (?, ?, ?)", (name, age, condition))
    conn.commit()
    conn.close()
    print(f"✅ Saved patient: {name}, Age: {age}, Condition: {condition}")

# ✅ Fetch patient details
def get_patient_details(name):
    conn = sqlite3.connect("patients.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, age, condition FROM patients WHERE name = ?", (name,))
    patient = cursor.fetchone()
    conn.close()
    if patient:
        return {"name": patient[0], "age": patient[1], "condition": patient[2]}
    return None

# ✅ Initialize database on import
initialize_db()

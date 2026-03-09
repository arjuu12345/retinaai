import sqlite3


def init_db():
    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    # Appointments table
    c.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        doctor TEXT,
        appointment_date TEXT,
        status TEXT
    )
    """)

    # Reports table
    c.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        prediction TEXT,
        confidence TEXT,
        file_path TEXT,
        date TEXT
    )
    """)

    # If the table already exists without date column, add it
    try:
        c.execute("ALTER TABLE reports ADD COLUMN date TEXT")
    except:
        pass

    conn.commit()
    conn.close()


# --------------------
# Appointment Functions
# --------------------

def add_appointment(patient, doctor, date):

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO appointments(patient_name,doctor,appointment_date,status) VALUES(?,?,?,?)",
        (patient, doctor, date, "Pending"),
    )

    conn.commit()
    conn.close()


def get_pending():

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("SELECT * FROM appointments WHERE status='Pending'")
    data = c.fetchall()

    conn.close()
    return data


def get_approved():

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("SELECT * FROM appointments WHERE status='Approved'")
    data = c.fetchall()

    conn.close()
    return data


def approve(id):

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("UPDATE appointments SET status='Approved' WHERE id=?", (id,))

    conn.commit()
    conn.close()


def delete_appointment(appointment_id):

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))

    conn.commit()
    conn.close()


# --------------------
# Report Functions
# --------------------

def save_report(patient, prediction, confidence, file_path):

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO reports(patient_name,prediction,confidence,file_path,date)
        VALUES(?,?,?,?,datetime('now'))
        """,
        (patient, prediction, confidence, file_path),
    )

    conn.commit()
    conn.close()


def get_reports():

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    c.execute("SELECT * FROM reports ORDER BY id DESC")
    data = c.fetchall()

    conn.close()
    return data


def get_reports():

    conn = sqlite3.connect("hospital.db")
    c = conn.cursor()

    # Ensure table exists
    c.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        prediction TEXT,
        confidence TEXT,
        file_path TEXT,
        date TEXT
    )
    """)

    c.execute("SELECT * FROM reports ORDER BY id DESC")
    data = c.fetchall()

    conn.close()
    return data

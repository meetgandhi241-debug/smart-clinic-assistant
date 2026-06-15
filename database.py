import sqlite3
import datetime

def create_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            age INTEGER,
            blood_group TEXT,
            phone TEXT,
            emergency_contact TEXT,
            address TEXT,
            medical_history TEXT,
            allergies TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            password TEXT,
            phone TEXT,
            specialization TEXT,
            clinic_name TEXT,
            clinic_address TEXT,
            clinic_id INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            doctor_name TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            queue_number INTEGER,
            status TEXT DEFAULT 'Pending'
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS family_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            member_name TEXT,
            relationship TEXT,
            age INTEGER,
            blood_group TEXT,
            allergies TEXT,
            existing_conditions TEXT,
            emergency_contact TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clinic_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER,
            open_time TEXT,
            close_time TEXT,
            max_appointments_per_day INTEGER,
            max_per_day INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            appointment_id INTEGER,
            clinic_id INTEGER,
            date TEXT,
            medicines TEXT,
            dosage TEXT,
            duration TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_type TEXT,
            user_id INTEGER,
            clinic_id INTEGER,
            title TEXT,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clinics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            address TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()

    # Ensure legacy databases have the 'status' column on appointments
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        # Attempt to add the status and queue_number columns if they don't exist
        try:
            cursor.execute("ALTER TABLE appointments ADD COLUMN status TEXT DEFAULT 'Pending'")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE appointments ADD COLUMN queue_number INTEGER")
        except Exception:
            pass
        conn.commit()
    except Exception:
        # Column likely already exists or DB locked; ignore
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Ensure clinic_settings has max_per_day column for compatibility
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE clinic_settings ADD COLUMN max_per_day INTEGER")
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Ensure doctors has phone/clinic columns for compatibility
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE doctors ADD COLUMN phone TEXT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE doctors ADD COLUMN clinic_name TEXT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE doctors ADD COLUMN clinic_address TEXT")
        except Exception:
            pass
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Ensure family_members has new health columns for compatibility
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE family_members ADD COLUMN allergies TEXT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE family_members ADD COLUMN existing_conditions TEXT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE family_members ADD COLUMN emergency_contact TEXT")
        except Exception:
            pass
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Ensure prescriptions has appointment_id and clinic_id columns for compatibility
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN appointment_id INTEGER")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE prescriptions ADD COLUMN clinic_id INTEGER")
        except Exception:
            pass
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Ensure notifications has clinic_id column for compatibility
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE notifications ADD COLUMN clinic_id INTEGER")
        except Exception:
            pass
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Ensure doctors has phone/clinic columns for compatibility
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE doctors ADD COLUMN phone TEXT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE doctors ADD COLUMN clinic_name TEXT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE doctors ADD COLUMN clinic_address TEXT")
        except Exception:
            pass
        try:
            cursor.execute("ALTER TABLE doctors ADD COLUMN clinic_id INTEGER")
        except Exception:
            pass
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Migrate existing doctor rows into clinics: create clinics based on clinic_name where clinic_id is null
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, clinic_name, clinic_address FROM doctors WHERE clinic_id IS NULL")
        rows = cursor.fetchall()
        for r in rows:
            did, cname, caddr = r[0], r[1], r[2]
            if not cname:
                # assign to a default clinic
                cname = f"Clinic_{did}"
            # check if clinic exists
            cursor.execute("SELECT id FROM clinics WHERE name=? LIMIT 1", (cname,))
            c = cursor.fetchone()
            if c:
                cid = c[0]
            else:
                cursor.execute("INSERT INTO clinics (name, address) VALUES (?, ?)", (cname, caddr))
                cid = cursor.lastrowid
            cursor.execute("UPDATE doctors SET clinic_id=? WHERE id=?", (cid, did))
        # Second-pass: handle any doctors with clinic_id NULL or 0 (robust backfill for legacy rows)
        cursor.execute("SELECT id, clinic_name, clinic_address FROM doctors WHERE clinic_id IS NULL OR clinic_id=0")
        rows2 = cursor.fetchall()
        for r in rows2:
            did, cname, caddr = r[0], r[1], r[2]
            if not cname:
                cname = f"Clinic_{did}"
            cursor.execute("SELECT id FROM clinics WHERE name=? LIMIT 1", (cname,))
            c = cursor.fetchone()
            if c:
                cid = c[0]
            else:
                cursor.execute("INSERT INTO clinics (name, address) VALUES (?, ?)", (cname, caddr))
                cid = cursor.lastrowid
            cursor.execute("UPDATE doctors SET clinic_id=? WHERE id=?", (cid, did))
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Normalize existing appointment statuses: convert NULL or legacy 'Waiting' to 'Pending'
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status='Pending' WHERE status IS NULL OR status='' OR status='Waiting'")
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Assign queue numbers for any appointments missing them (per doctor + date)
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT doctor_name, appointment_date FROM appointments WHERE queue_number IS NULL GROUP BY doctor_name, appointment_date")
        missing_groups = cursor.fetchall()
        for grp in missing_groups:
            doc = grp[0]
            appt_date = grp[1]
            # find current max queue number for this doctor/date
            cursor.execute("SELECT COALESCE(MAX(queue_number), 0) FROM appointments WHERE doctor_name=? AND appointment_date=?", (doc, appt_date))
            max_q = cursor.fetchone()[0] or 0

            # select rows lacking queue_number in a deterministic order
            cursor.execute("SELECT id FROM appointments WHERE doctor_name=? AND appointment_date=? AND (queue_number IS NULL) ORDER BY appointment_time, id", (doc, appt_date))
            rows = cursor.fetchall()
            for i, r in enumerate(rows, start=1):
                new_q = max_q + i
                cursor.execute("UPDATE appointments SET queue_number=? WHERE id=?", (new_q, r[0]))

        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Ensure appointments has clinic_id column for compatibility
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            cursor.execute("ALTER TABLE appointments ADD COLUMN clinic_id INTEGER")
        except Exception:
            pass
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def register_patient(name, email, password, age=None, blood_group=None, phone=None, emergency_contact=None, address=None, medical_history=None, allergies=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO patients (name, email, password, age, blood_group, phone, emergency_contact, address, medical_history, allergies) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (name, email, password, age, blood_group, phone, emergency_contact, address, medical_history, allergies)
    )

    conn.commit()
    conn.close()


def register_doctor(name, email, password, specialization):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Prevent duplicate email
    cursor.execute("SELECT id FROM doctors WHERE email=? LIMIT 1", (email,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Email already registered")

    cursor.execute(
        "INSERT INTO doctors (name, email, password, phone, specialization, clinic_name, clinic_address) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, email, password, None, specialization, None, None)
    )

    conn.commit()
    conn.close()


def get_doctor_by_email(email):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE email=? LIMIT 1", (email,))
    doc = cursor.fetchone()
    conn.close()
    return doc


def create_clinic(name, address=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # ensure uniqueness by name
    cursor.execute("SELECT id FROM clinics WHERE name=? LIMIT 1", (name,))
    row = cursor.fetchone()
    if row:
        cid = row[0]
    else:
        cursor.execute("INSERT INTO clinics (name, address) VALUES (?, ?)", (name, address))
        cid = cursor.lastrowid
    conn.commit()
    conn.close()
    return cid


def get_clinic_by_id(clinic_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address, created_at FROM clinics WHERE id=? LIMIT 1", (clinic_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_clinics():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address FROM clinics ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def login_patient(email, password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE email=? AND password=?",
        (email, password,)
    )

    patient = cursor.fetchone()

    conn.close()

    return patient


def login_doctor(email, password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM doctors WHERE email=? AND password=?",
        (email, password)
    )

    doctor = cursor.fetchone()

    conn.close()

    return doctor


def create_appointment(patient_name, doctor_name, appointment_date, appointment_time, status='Pending', clinic_id=None):
    """Create appointment and assign next queue number for that doctor and date.

    Default status is 'Pending'.
    """
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Determine next queue number for this doctor and date
    # Determine next queue number for this doctor and date (and clinic if provided)
    if clinic_id is None:
        cursor.execute(
            "SELECT COALESCE(MAX(queue_number), 0) FROM appointments WHERE doctor_name=? AND appointment_date=?",
            (doctor_name, appointment_date)
        )
    else:
        cursor.execute(
            "SELECT COALESCE(MAX(queue_number), 0) FROM appointments WHERE doctor_name=? AND appointment_date=? AND clinic_id=?",
            (doctor_name, appointment_date, clinic_id)
        )
    row = cursor.fetchone()
    next_queue = (row[0] or 0) + 1

    if clinic_id is None:
        cursor.execute(
            "INSERT INTO appointments (patient_name, doctor_name, appointment_date, appointment_time, queue_number, status) VALUES (?, ?, ?, ?, ?, ?)",
            (patient_name, doctor_name, appointment_date, appointment_time, next_queue, status)
        )
    else:
        cursor.execute(
            "INSERT INTO appointments (patient_name, doctor_name, appointment_date, appointment_time, queue_number, status, clinic_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (patient_name, doctor_name, appointment_date, appointment_time, next_queue, status, clinic_id)
        )

    conn.commit()
    conn.close()


def get_queue_for_doctor_date(doctor_name, appointment_date, clinic_id=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    if clinic_id is None:
        cursor.execute(
            "SELECT id, patient_name, doctor_name, appointment_date, appointment_time, queue_number, status FROM appointments WHERE doctor_name=? AND appointment_date=? ORDER BY queue_number ASC",
            (doctor_name, appointment_date)
        )
    else:
        cursor.execute(
            "SELECT id, patient_name, doctor_name, appointment_date, appointment_time, queue_number, status FROM appointments WHERE doctor_name=? AND appointment_date=? AND clinic_id=? ORDER BY queue_number ASC",
            (doctor_name, appointment_date, clinic_id)
        )

    appointments = cursor.fetchall()
    conn.close()
    return appointments


def get_current_active_queue_number(doctor_name, appointment_date, clinic_id=None):
    """Return the queue_number of the appointment currently 'In Progress', or None."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if clinic_id is None:
        cursor.execute(
            "SELECT queue_number FROM appointments WHERE doctor_name=? AND appointment_date=? AND status='In Progress' ORDER BY queue_number LIMIT 1",
            (doctor_name, appointment_date)
        )
    else:
        cursor.execute(
            "SELECT queue_number FROM appointments WHERE doctor_name=? AND appointment_date=? AND clinic_id=? AND status='In Progress' ORDER BY queue_number LIMIT 1",
            (doctor_name, appointment_date, clinic_id)
        )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def mark_next_patient(doctor_name, appointment_date, clinic_id=None):
    """Advance the queue: mark current In Progress as Completed, and next Pending as In Progress."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    try:
        # Complete any existing In Progress entries for this doctor/date
        if clinic_id is None:
            cursor.execute("UPDATE appointments SET status='Completed' WHERE doctor_name=? AND appointment_date=? AND status='In Progress'", (doctor_name, appointment_date))
        else:
            cursor.execute("UPDATE appointments SET status='Completed' WHERE doctor_name=? AND appointment_date=? AND clinic_id=? AND status='In Progress'", (doctor_name, appointment_date, clinic_id))

        # Find next pending appointment by queue_number
        if clinic_id is None:
            cursor.execute("SELECT id FROM appointments WHERE doctor_name=? AND appointment_date=? AND status='Pending' ORDER BY queue_number LIMIT 1", (doctor_name, appointment_date))
        else:
            cursor.execute("SELECT id FROM appointments WHERE doctor_name=? AND appointment_date=? AND clinic_id=? AND status='Pending' ORDER BY queue_number LIMIT 1", (doctor_name, appointment_date, clinic_id))
        nxt = cursor.fetchone()
        if nxt:
            cursor.execute("UPDATE appointments SET status='In Progress' WHERE id=?", (nxt[0],))

        conn.commit()
    finally:
        conn.close()


def get_doctors():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    conn.close()
    return doctors


def get_appointments_by_doctor(doctor_name, clinic_id=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    if clinic_id is None:
        cursor.execute(
            "SELECT id, patient_name, doctor_name, appointment_date, appointment_time, queue_number, status FROM appointments WHERE doctor_name=? ORDER BY appointment_date, queue_number, appointment_time",
            (doctor_name,)
        )
    else:
        cursor.execute(
            "SELECT id, patient_name, doctor_name, appointment_date, appointment_time, queue_number, status FROM appointments WHERE doctor_name=? AND clinic_id=? ORDER BY appointment_date, queue_number, appointment_time",
            (doctor_name, clinic_id)
        )

    appointments = cursor.fetchall()
    conn.close()
    return appointments


def get_appointments_by_patient(patient_name):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, patient_name, doctor_name, appointment_date, appointment_time, queue_number, status, clinic_id FROM appointments WHERE patient_name=? ORDER BY appointment_date, appointment_time",
        (patient_name,)
    )

    appointments = cursor.fetchall()
    conn.close()
    return appointments


def update_appointment_status(appointment_id, status):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    try:
        # If setting an appointment to In Progress, ensure only one In Progress exists per doctor/date
        if status == 'In Progress':
            cursor.execute("SELECT doctor_name, appointment_date, clinic_id FROM appointments WHERE id=? LIMIT 1", (appointment_id,))
            row = cursor.fetchone()
            if row:
                doctor_name, appointment_date, clinic_id = row[0], row[1], row[2] if len(row) > 2 else None
                # mark any existing in-progress appointments for this doctor/date and clinic as Completed
                if clinic_id is None:
                    cursor.execute("UPDATE appointments SET status='Completed' WHERE doctor_name=? AND appointment_date=? AND status='In Progress'", (doctor_name, appointment_date))
                else:
                    cursor.execute("UPDATE appointments SET status='Completed' WHERE doctor_name=? AND appointment_date=? AND clinic_id=? AND status='In Progress'", (doctor_name, appointment_date, clinic_id))

        cursor.execute(
            "UPDATE appointments SET status=? WHERE id=?",
            (status, appointment_id)
        )
        conn.commit()
    finally:
        conn.close()


def set_clinic_settings(doctor_id, open_time, close_time, max_appointments_per_day):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM clinic_settings WHERE doctor_id=?", (doctor_id,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            "UPDATE clinic_settings SET open_time=?, close_time=?, max_appointments_per_day=? WHERE doctor_id=?",
            (open_time, close_time, max_appointments_per_day, doctor_id)
        )
    else:
        cursor.execute(
            "INSERT INTO clinic_settings (doctor_id, open_time, close_time, max_appointments_per_day) VALUES (?, ?, ?, ?)",
            (doctor_id, open_time, close_time, max_appointments_per_day)
        )

    conn.commit()
    conn.close()


def save_clinic_settings(doctor_id, open_time, close_time, max_per_day):
    """Save clinic settings, stored in both `max_per_day` and `max_appointments_per_day` for compatibility."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM clinic_settings WHERE doctor_id=?", (doctor_id,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            "UPDATE clinic_settings SET open_time=?, close_time=?, max_appointments_per_day=?, max_per_day=? WHERE doctor_id=?",
            (open_time, close_time, max_per_day, max_per_day, doctor_id)
        )
    else:
        cursor.execute(
            "INSERT INTO clinic_settings (doctor_id, open_time, close_time, max_appointments_per_day, max_per_day) VALUES (?, ?, ?, ?, ?)",
            (doctor_id, open_time, close_time, max_per_day, max_per_day)
        )

    conn.commit()
    conn.close()


def get_clinic_settings(doctor_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Return a consistent tuple: (id, doctor_id, open_time, close_time, max_per_day)
    cursor.execute(
        "SELECT id, doctor_id, open_time, close_time, COALESCE(max_per_day, max_appointments_per_day, 0) as max_per_day FROM clinic_settings WHERE doctor_id=? LIMIT 1",
        (doctor_id,)
    )
    settings = cursor.fetchone()
    conn.close()
    return settings


def get_appointments_count_by_doctor_date(doctor_name, appointment_date):
    # backward-compatible: optional clinic-aware calls may pass clinic_id by embedding it in doctor_name tuple
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM appointments WHERE doctor_name=? AND appointment_date=?",
        (doctor_name, appointment_date)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_appointments_count_by_doctor_date_status(doctor_name, appointment_date, status, clinic_id=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if clinic_id is None:
        cursor.execute(
            "SELECT COUNT(*) FROM appointments WHERE doctor_name=? AND appointment_date=? AND status=?",
            (doctor_name, appointment_date, status)
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM appointments WHERE doctor_name=? AND appointment_date=? AND status=? AND clinic_id=?",
            (doctor_name, appointment_date, status, clinic_id)
        )
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_patient_by_id(patient_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id=?",
        (patient_id,)
    )

    patient = cursor.fetchone()
    conn.close()
    return patient


def update_patient_profile(patient_id, age=None, blood_group=None, phone=None, emergency_contact=None, address=None, medical_history=None, allergies=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE patients SET age=?, blood_group=?, phone=?, emergency_contact=?, address=?, medical_history=?, allergies=? WHERE id=?",
        (age, blood_group, phone, emergency_contact, address, medical_history, allergies, patient_id)
    )

    conn.commit()
    conn.close()


def get_patient_profile(patient_name):
    """Return the first patient record matching the given name or None if not found.

    patient tuple schema: (id, name, email, password, age, blood_group, phone, emergency_contact, address, medical_history, allergies)
    """
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM patients WHERE name=? LIMIT 1",
            (patient_name,)
        )

        patient = cursor.fetchone()
        return patient
    except Exception:
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass


def create_prescription(patient_id, doctor_id, appointment_id=None, date=None, medicines=None, dosage=None, duration=None, notes=None, clinic_id=None):
    """Insert a prescription record. `medicines` is a text blob (newline-separated or comma-separated).

    `appointment_id` links the prescription to a specific appointment if provided.
    """
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if date is None:
        date = datetime.date.today().isoformat()

    # If caller did not provide clinic_id, attempt to infer it from the linked appointment
    if clinic_id is None and appointment_id is not None:
        try:
            cursor.execute("SELECT clinic_id FROM appointments WHERE id=? LIMIT 1", (appointment_id,))
            row = cursor.fetchone()
            if row:
                clinic_id = row[0]
        except Exception:
            clinic_id = None

    cursor.execute(
        "INSERT INTO prescriptions (patient_id, doctor_id, appointment_id, clinic_id, date, medicines, dosage, duration, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (patient_id, doctor_id, appointment_id, clinic_id, date, medicines, dosage, duration, notes)
    )

    conn.commit()
    conn.close()


def get_prescriptions_by_patient(patient_id):
    """Return prescriptions for a patient ordered newest-first. Includes doctor name via join."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT p.id, p.patient_id, p.doctor_id, p.date, p.medicines, p.dosage, p.duration, p.notes, p.created_at, d.name as doctor_name FROM prescriptions p LEFT JOIN doctors d ON p.doctor_id=d.id WHERE p.patient_id=? ORDER BY p.created_at DESC",
        (patient_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def create_notification(user_type, user_id, title, message, is_read=False, clinic_id=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    if clinic_id is None:
        cursor.execute(
            "INSERT INTO notifications (user_type, user_id, title, message, is_read) VALUES (?, ?, ?, ?, ?)",
            (user_type, user_id, title, message, 1 if is_read else 0)
        )
    else:
        cursor.execute(
            "INSERT INTO notifications (user_type, user_id, clinic_id, title, message, is_read) VALUES (?, ?, ?, ?, ?, ?)",
            (user_type, user_id, clinic_id, title, message, 1 if is_read else 0)
        )
    conn.commit()
    conn.close()


def get_notifications(user_type, user_id, unread_only=False, limit=None, clinic_id=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Return columns in a stable order compatible with UI and tests:
    # (id, user_type, user_id, title, message, is_read, created_at, clinic_id)
    sql = "SELECT id, user_type, user_id, title, message, is_read, created_at, clinic_id FROM notifications WHERE user_type=? AND user_id=?"
    params = [user_type, user_id]
    if unread_only:
        sql += " AND is_read=0"
    if clinic_id is not None:
        sql += " AND clinic_id=?"
        params.append(clinic_id)
    sql += " ORDER BY created_at DESC"
    if limit:
        sql += " LIMIT ?"
        params.append(limit)
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return rows


def mark_notification_read(notification_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read=1 WHERE id=?", (notification_id,))
    conn.commit()
    conn.close()


def mark_all_notifications_read(user_type, user_id, clinic_id=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    if clinic_id is None:
        cursor.execute("UPDATE notifications SET is_read=1 WHERE user_type=? AND user_id=?", (user_type, user_id))
    else:
        cursor.execute("UPDATE notifications SET is_read=1 WHERE user_type=? AND user_id=? AND clinic_id=?", (user_type, user_id, clinic_id))
    conn.commit()
    conn.close()


def get_unread_count(user_type, user_id, clinic_id=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    if clinic_id is None:
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_type=? AND user_id=? AND is_read=0", (user_type, user_id))
    else:
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_type=? AND user_id=? AND clinic_id=? AND is_read=0", (user_type, user_id, clinic_id))
    cnt = cursor.fetchone()[0]
    conn.close()
    return cnt


def add_family_member(patient_id, member_name, relationship, age=None, blood_group=None, allergies=None, existing_conditions=None, emergency_contact=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO family_members (patient_id, member_name, relationship, age, blood_group, allergies, existing_conditions, emergency_contact) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (patient_id, member_name, relationship, age, blood_group, allergies, existing_conditions, emergency_contact)
    )

    conn.commit()
    conn.close()


def get_family_members_by_patient(patient_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, patient_id, member_name, relationship, age, blood_group, allergies, existing_conditions, emergency_contact FROM family_members WHERE patient_id=?",
        (patient_id,)
    )

    members = cursor.fetchall()
    conn.close()
    return members


def delete_family_member(member_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM family_members WHERE id=?",
        (member_id,)
    )

    conn.commit()
    conn.close()


def update_family_member(member_id, member_name=None, relationship=None, age=None, blood_group=None, allergies=None, existing_conditions=None, emergency_contact=None):
    """Update fields for a family member. Only non-None values will be updated."""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Build dynamic update
    fields = []
    params = []
    if member_name is not None:
        fields.append("member_name=?")
        params.append(member_name)
    if relationship is not None:
        fields.append("relationship=?")
        params.append(relationship)
    if age is not None:
        fields.append("age=?")
        params.append(age)
    if blood_group is not None:
        fields.append("blood_group=?")
        params.append(blood_group)
    if allergies is not None:
        fields.append("allergies=?")
        params.append(allergies)
    if existing_conditions is not None:
        fields.append("existing_conditions=?")
        params.append(existing_conditions)
    if emergency_contact is not None:
        fields.append("emergency_contact=?")
        params.append(emergency_contact)

    if not fields:
        conn.close()
        return

    params.append(member_id)
    sql = f"UPDATE family_members SET {', '.join(fields)} WHERE id=?"
    cursor.execute(sql, tuple(params))
    conn.commit()
    conn.close()


# Ensure database and migrations are applied when module is imported
try:
    create_database()
except Exception:
    # If the environment prevents running migrations at import, tests or callers
    # that need migrations should call create_database() explicitly.
    pass


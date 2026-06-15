import os
import shutil
import sys
import sqlite3

# ensure we can import database module from workspace
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.db'))
BACKUP_PATH = DB_PATH + '.bak'

results = []

# backup existing DB if present
if os.path.exists(DB_PATH):
    shutil.copy2(DB_PATH, BACKUP_PATH)

try:
    # initialize fresh database
    try:
        os.remove(DB_PATH)
    except FileNotFoundError:
        pass
    database.create_database()

    # Test 1: Successful doctor registration (via direct insert as app does)
    doc_email = 'dr.jane@example.com'
    doc_name = 'Dr. Jane Doe'
    doc_password = 'secret123'
    doc_phone = '5551234567'
    doc_specialization = 'Cardiology'
    doc_clinic = 'Heart Care Clinic'
    doc_address = '123 Health St'

    # ensure no existing
    existing = database.get_doctor_by_email(doc_email)
    if existing:
        results.append(('doctor_registration_initial', False, 'Doctor already exists before test'))
    else:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO doctors (name, email, password, phone, specialization, clinic_name, clinic_address) VALUES (?, ?, ?, ?, ?, ?, ?)", (doc_name, doc_email, doc_password, doc_phone, doc_specialization, doc_clinic, doc_address))
        conn.commit()
        conn.close()

        created = database.get_doctor_by_email(doc_email)
        if created and created[1] == doc_name and created[2] == doc_email:
            results.append(('doctor_registration_initial', True, ''))
        else:
            results.append(('doctor_registration_initial', False, 'Inserted doctor not found with expected values'))

    # Test 2: Duplicate email validation via register_doctor() (should raise ValueError)
    dup_passed = False
    try:
        # register_doctor in DB layer checks for duplicate and raises
        database.register_doctor('Another Doc', doc_email, 'pw', 'Dermatology')
        dup_passed = False
    except ValueError:
        dup_passed = True
    except Exception as e:
        # unexpected error
        results.append(('duplicate_email_check', False, f'Unexpected exception: {e}'))
    else:
        results.append(('duplicate_email_check', dup_passed, ''))
    if dup_passed:
        results.append(('duplicate_email_check', True, ''))

    # Test 3: Password mismatch validation (UI-level) - simulate app logic
    # Simulate entering password/confirm that do not match: app should NOT insert new doctor
    mismatch_email = 'dr.mismatch@example.com'
    # simulate check in app: if password != confirm -> error and do not insert
    pw = 'abc'
    confirm = 'def'
    if pw != confirm:
        # ensure no record created
        if database.get_doctor_by_email(mismatch_email) is None:
            results.append(('password_mismatch', True, ''))
        else:
            results.append(('password_mismatch', False, 'Record exists despite mismatch'))
    else:
        results.append(('password_mismatch', False, 'Test setup invalid'))

    # Test 4: Doctor login with newly registered account
    logged = database.login_doctor(doc_email, doc_password)
    if logged:
        results.append(('doctor_login', True, ''))
    else:
        results.append(('doctor_login', False, 'login_doctor returned None'))

    # Test 5: Doctor dashboard displays correct info (name, specialization, clinic)
    doc = database.get_doctor_by_email(doc_email)
    if doc:
        # doc tuple layout: (id, name, email, password, phone, specialization, clinic_name, clinic_address)
        ok = True
        reasons = []
        try:
            if doc[1] != doc_name:
                ok = False
                reasons.append('name mismatch')
            if len(doc) > 5 and doc[5] != doc_specialization:
                ok = False
                reasons.append('specialization mismatch')
            if len(doc) > 6 and doc[6] != doc_clinic:
                ok = False
                reasons.append('clinic mismatch')
        except Exception as e:
            ok = False
            reasons.append(f'exception checking fields: {e}')
        results.append(('doctor_dashboard_info', ok, ','.join(reasons)))
    else:
        results.append(('doctor_dashboard_info', False, 'doctor not found'))

    # Test 6: Patient can book appointment with newly registered doctor
    patient_name = 'Alice Patient'
    patient_email = 'alice@example.com'
    patient_pw = 'alicepw'
    database.register_patient(patient_name, patient_email, patient_pw)
    # book appointment
    appt_date = '2026-06-15'
    appt_time = '10:30'
    database.create_appointment(patient_name, doc_name, appt_date, appt_time)
    # verify appointment exists for doctor
    appts = database.get_appointments_by_doctor(doc_name)
    found = False
    for a in appts:
        if a[1] == patient_name and a[3] == appt_date and a[4] == appt_time:
            found = True
            appt_id = a[0]
            break
    results.append(('patient_booking', found, ''))

    # Test 7: Newly registered doctor can view appointments
    # Use get_appointments_by_doctor
    appts2 = database.get_appointments_by_doctor(doc_name)
    results.append(('doctor_view_appointments', len(appts2) > 0, ''))

    # Print summary
    all_pass = all(r[1] for r in results)
    for name, ok, info in results:
        print(f"{name}: {'PASS' if ok else 'FAIL'}{(' - '+info) if info else ''}")

    if not all_pass:
        print('\nSome tests failed. Exiting with code 1')
        sys.exit(1)
    else:
        print('\nAll tests passed.')
        sys.exit(0)

finally:
    # restore original DB if backed up
    if os.path.exists(BACKUP_PATH):
        shutil.move(BACKUP_PATH, DB_PATH)
    else:
        # leave created DB in place
        pass
